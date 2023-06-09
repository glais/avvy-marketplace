from django.contrib import admin
from . import models


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
	list_display = [
		'name',
		'expiry_date',
	]


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
	pass
