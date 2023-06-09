from background_task import background
from background_task.models import Task
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from . import models
import requests


#
# Related to syncing name registrations
#

@background
def sync_domain_registration_data_for_name_batch(domain_ids):
	domains = models.Domain.objects.filter(pk__in=domain_ids)
	names = [d.name for d in domains]
	print(f'Syncing domain batch {names}')
	query = "{"
	for i, domain in enumerate(domains):
		name = domain.name
		query += f"""
		q{i}: domains(search: "{name}") {{
			name
			hash
			expiry
		}}
		"""
	query += "}"
	payload = {
		'query': query
	}
	res = requests.post('https://api.avvy.domains/graphql', json=payload)
	res_data = res.json()['data']
	for i, domain in enumerate(domains):
		data = res_data[f'q{i}']
		if len(data) == 0:
			# domain isn't registered
			pass
		else:
			data = data[0]
			domain.hash = data['hash']
			domain.expiry_date = data['expiry']
		domain.last_updated_at = timezone.now()
		domain.save()


@background
def sync_domain_registration_data():
	domains = models.Domain.objects.filter(name__isnull=False)
	now = timezone.now()
	batch = []
	update_threshold_seconds = 60 # how many seconds before we consider the record stale?
	max_batch_size = 100
	for domain in domains:
		if not domain.last_updated or now - domain.last_updated > timedelta(seconds=update_threshold_seconds):
			batch.append(domain.id)

			# if the batch is full, save the task
			if len(batch) >= max_batch_size:
				sync_domain_registration_data_for_name_batch(batch)
				batch = []
	
	# save the final task
	if len(batch) > 0:
		sync_domain_registration_data_for_name_batch(batch)


# 
# Related to syncing Opensea listings 
#
@background
def sync_opensea_listings_cleanup():
	sync_status = models.SyncStatus.get_solo()
	stale_listings = models.Listing.objects.filter(
		last_update=sync_status.opensea_last_sync,
		marketplace=models.Listing.MARKETPLACES['OPENSEA']
	)
	stale_listings.delete()


@background
def sync_opensea_listings_page(cursor=None):
	headers = {
		'X-API-KEY': settings.OPENSEA_API_KEY
	}
	params = {
		'limit': 100,
	}
	if cursor is not None:
		params['next'] = cursor
	res = requests.get('https://api.opensea.io/v2/listings/collection/avvy-domains-avax/all', headers=headers, params=params)

	if res.status_code == 429:
		# rate limit, come back in 1 minute
		sync_opensea_listings_page(cursor, schedule=60)
		return

	data = res.json()

	if 'listings' not in data:
		print('Something went wrong, tf happened?')
		import ipdb; ipdb.set_trace()
	
	listings = data['listings']

	for _listing in listings:
		try:
			params = _listing.get('protocol_data', {}).get('parameters', {})
			offer = params.get('offer', {})
			if len(offer) > 1:
				#import ipdb; ipdb.set_trace()
				raise Exception("More than one item in opensea listing.. wat do?")
			offer = offer[0]

			# get token id
			token_id = offer['identifierOrCriteria']

			# get seller
			seller = params['offerer']

			try:
				domain, _ = models.Domain.objects.get_or_create(
					hash=token_id
				)
			except:
				import ipdb; ipdb.set_trace()
				pass

			listing, _ = models.Listing.objects.get_or_create(
				marketplace=models.Listing.MARKETPLACES['OPENSEA'],
				seller=seller,
				domain=domain
			)
			
			# get price
			price = _listing['price']['current']
			listing.price = price['value']
			listing.currency = price['currency']
			listing.decimals = price['decimals']
			listing.save()
		except Exception as e:
			#import ipdb; ipdb.set_trace()
			raise e

	# load next page
	if data['next']:
		sync_opensea_listings_page(data['next'])
	else:
		sync_opensea_listings_cleanup()


@background
def sync_opensea_listings():
	""" this syncs all opensea listings via the retrieve_all_listings route """
	""" WARNING: we don't pay attention to rate limiting here :D that will
	cause problems at some point. """
	sync_status = models.SyncStatus.get_solo()
	now = timezone.now()
	update_threshold_seconds = 60 * 5
	if sync_status.opensea_last_sync is None or now - sync_status.opensea_last_sync > timedelta(seconds=update_threshold_seconds):
		sync_opensea_listings_page()
		sync_status.opensea_last_sync = now
		sync_status.save()

@background
def sync():
	# Master sync process, which
	# initializes all of the child processes
	sync_domain_registration_data()
	sync_opensea_listings()

	# schedule another sync
	sync(schedule=60*5)


# start the initial sync task.
if Task.objects.filter(task_name='core.tasks.sync').count() == 0:
	sync()
