from django.contrib import admin
from . import models


@admin.register(models.Domain)
class DomainAdmin(admin.ModelAdmin):
	pass


@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
	pass
