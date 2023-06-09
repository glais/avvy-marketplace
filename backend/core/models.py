from django.db import models
from solo.models import SingletonModel
from datetime import datetime


class Domain(models.Model):
	hash = models.CharField(max_length=500, null=True, blank=True)
	name = models.CharField(max_length=200, null=True, blank=True)
	expiry_date = models.DateTimeField(null=True, blank=True)
	last_updated = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.name
	
	def is_registered(self):
		return self.expiry_date is not None
	
	def is_expired(self):
		now = datetime.now()
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
		domains = self.domain_list.splitlines()

		# add missing domains
		for _domain in domains:
			domain, _ = Domain.objects.get_or_create(name=_domain)
			if not self.domains.filter(pk=domain.pk).exists():
				self.domains.add(domain)

		# remove the ones that we don't want in the list
		to_remove = set([d.name for d in self.domains.all()]) - set(domains)
		for domain in self.domains.filter(name__in=to_remove):
			self.domains.remove(domain)
			
		return super().save(*args, **kwargs)


class SyncStatus(SingletonModel):
	domain_sync_block = models.CharField(default='14909991', max_length=200)

	def __str__(self):
		return "Sync Status"

	class Meta:
		verbose_name = 'Sync Status'
