from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404
from . import models


class CollectionView(View):
	def get(self, *args, **kwargs):
		collection = get_object_or_404(models.Collection, slug=self.kwargs.get('slug'))
		domains = collection.domains.all().order_by('name')
		return JsonResponse({
			'data': [{
				'DomainName': domain.name,
				'DomainStatus': 'Registered',
				'ExpiryDate': domain.expiry_date,
			} for domain in domains]
		})
