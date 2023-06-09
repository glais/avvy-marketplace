from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404
from . import models


class CollectionView(View):
	def get(self, *args, **kwargs):
		collection = get_object_or_404(models.Collection, slug=self.kwargs.get('slug'))
		domains = collection.domains.all().order_by('name')
		data = []
		for domain in domains:
			status = None
			if not domain.is_registered() or domain.is_expired():
				status = 'Available'
			else:
				status = 'Registered'
			data.append({
				'DomainName': domain.name,
				'DomainStatus': 'Registered' if domain.is_registered() else 'Available',
				'ExpiryDate': 'Expired' if domain.is_expired() else domain.expiry_date,
			})
		return JsonResponse({
			'data': data
		})
