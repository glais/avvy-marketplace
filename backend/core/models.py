from django.db import models
from solo.models import SingletonModel
from django.utils import timezone
from decimal import Decimal as D
from . import helpers


class Domain(models.Model):
	hash = models.CharField(max_length=500, null=True, blank=True)
	name = models.CharField(max_length=200, null=True, blank=True)
	expiry_date = models.DateTimeField(null=True, blank=True)
	last_updated = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.name or self.hash
	
	def is_registered(self):
		return self.expiry_date is not None
	
	def is_expired(self):
		now = timezone.now()
		if self.expiry_date is None: return False
		return now > self.expiry_date


class Collection(models.Model):
	name = models.CharField(max_length=200)
	slug = models.SlugField(max_length=200)
	domains = models.ManyToManyField(Domain, editable=False)

	def __str__(self):
		return self.name
	
	# We put the name_list here just to hack
	# Django Admin. This puts a file field in
	# the admin panel, and when we upload a .txt
	# list, we can parse through it and create 
	# the ManyToMany records that we need.
	domain_list = models.TextField(null=True, blank=True, help_text="To edit this collection, save the list of domains here.")
	def save(self, *args, **kwargs):
		out = super().save(*args, **kwargs)
		domains = self.domain_list.splitlines()

		# add missing domains
		for _domain in domains:

			# this is fucking slow because it hits the RPC for each domain
			# in series.. need to fix this to multicall or something.
			hash = helpers.get_hash(_domain)

			domain, _ = Domain.objects.get_or_create(
				hash=hash
			)
			domain.name = _domain
			domain.save()
			if not self.domains.filter(pk=domain.pk).exists():
				self.domains.add(domain)

		# remove the ones that we don't want in the list
		to_remove = set([d.name for d in self.domains.all()]) - set(domains)
		for domain in self.domains.filter(name__in=to_remove):
			self.domains.remove(domain)
			
		return out


class SyncStatus(SingletonModel):
	opensea_last_sync = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return "Sync Status"

	class Meta:
		verbose_name = 'Sync Status'


class Listing(models.Model):
	MARKETPLACES = {
		'OPENSEA': 1
	}
	MARKETPLACE_CHOICES = [
		(k, v,) for k, v in MARKETPLACES.items()
	]
	marketplace = models.IntegerField(choices=MARKETPLACE_CHOICES)
	domain = models.ForeignKey(Domain, null=True, blank=True, on_delete=models.CASCADE)
	seller = models.CharField(max_length=500, null=True, blank=True)
	price = models.CharField(max_length=100, null=True, blank=True)
	currency = models.CharField(max_length=50, default='AVAX')
	decimals = models.IntegerField(default=0)

	last_update = models.DateTimeField(auto_now=True)

	def token_id(self):
		return self.domain.hash

	def price_pretty(self):
		if not self.price: return None
		print(self.price)
		print(self.decimals)
		price_with_precision = '%.4f' % (D(self.price) / D(self.decimals))
		currency = self.currency
		return f'{price_with_precision} {currency}'
