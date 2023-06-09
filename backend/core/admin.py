from django.contrib import admin
from solo.admin import SingletonModelAdmin
from . import models


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
	list_display = [
		'hash',
		'name',
		'expiry_date',
	]


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
	pass


@admin.register(models.Listing)
class ListingAdmin(admin.ModelAdmin):
	list_display = [
		'token_id',
		'seller',
		'marketplace',
		'price',
		'currency'
	]


admin.site.register(models.SyncStatus, SingletonModelAdmin)
