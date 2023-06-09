from django.db import models


class Domain(models.Model):
	name = models.CharField(max_length=200)
	expiry_date = models.DateTimeField(null=True, blank=True)

	def __str__(self):
		return self.name


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

