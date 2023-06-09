from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import get_object_or_404
from . import models


class CollectionView(View):
	def get(self, *args, **kwargs):
		collection = get_object_or_404(models.Collection, slug=self.kwargs.get('slug'))
		domains = collection.domains.all().order_by('name')
		data = []
		listings = []

		def build_listings_dict(qs):
			return {
				listing.domain.id: listing for listing in qs
			}

		opensea_listings = build_listings_dict(
			models.Listing.objects.filter(
				domain__in=domains,
				marketplace=models.Listing.MARKETPLACES['OPENSEA']
			)
		)

		for domain in domains:
			status = None
			has_listing = domain.id in opensea_listings

			if has_listing:
				status = 'For Sale'
			elif not domain.is_registered() or domain.is_expired():
				status = 'Available'
			else:
				status = 'Registered'

			row = {
				'DomainName': domain.name,
				'DomainStatus': status,
				'ExpiryDate': 'Expired' if domain.is_expired() else domain.expiry_date,
			}

			if domain.id in opensea_listings:
				row['OpenseaPrice'] = opensea_listings[domain.id].price
				row['OpenseaCurrency'] = opensea_listings[domain.id].currency
				row['OpenseaDecimals'] = opensea_listings[domain.id].decimals
			
			data.append(row)
			
		return JsonResponse({
			'name': collection.name,
			'domains': data,
		})
