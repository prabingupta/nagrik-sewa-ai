from django.contrib import admin
from .models import Service, Query


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["name", "name_nepali", "is_popular", "created_at"]
    search_fields = ["name", "name_nepali"]
    list_filter = ["is_popular"]


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ["question", "service", "language", "created_at"]
    list_filter = ["language"]
    readonly_fields = ["answer_json", "created_at"]