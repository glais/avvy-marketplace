from background_task import background
from web3.middleware import geth_poa_middleware
from web3 import Web3
from . import contracts, models
from datetime import datetime
import requests


# We're not actually pulling data from the chain
# Instead we're pulling from the centralized
# avvy indexer for simplicity. In the future
# data could be pulled directly from RPC.
def get_w3(network_id=None):
	if network_id is None: network_id = 43114
	rpc_url = {
		43113: 'https://api.avax-test.network/ext/bc/C/rpc',
		43114: 'https://api.avax.network/ext/bc/C/rpc',
	}[network_id]
	provider = Web3.HTTPProvider(rpc_url)
	w3 = Web3(provider)
	w3.middleware_onion.inject(geth_poa_middleware, layer=0)
	return w3


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
		domain.last_updated_at = datetime.now()
		domain.save()



@background
def sync_domain_registration_data_for_name(domain_id):
	domain = models.Domain.objects.get(pk=domain_id)
	name = domain.name
	print(f'Syncing {name}')
	query = f"""
	{{
		domains(search: "{name}") {{
			name
			hash
			expiry
		}}
	}}
	"""
	payload = {
		'query': query
	}
	res = requests.post('https://api.avvy.domains/graphql', json=payload)
	data = res.json()['data']['domains']
	if len(data) == 0:
		# domain isn't registered
		pass
	else:
		data = data[0]
		domain.hash = data['hash']
		domain.expiry_date = data['expiry']
	domain.last_updated_at = datetime.now()
	domain.save()


@background
def sync_domain_registration_data():
	domains = models.Domain.objects.all()
	now = datetime.now()
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
	sync_domain_registration_data_for_name_batch(batch)

def sync():
	# Master sync process, which
	# initializes all of the child processes
	sync_domain_registration_data()

	# schedule another sync
	#sync(schedule=60*5)
