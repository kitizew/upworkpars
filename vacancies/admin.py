from django.contrib import admin
from .models import Vacancy

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ("title", "budget", "tier", "client_country", "published_at")
    search_fields = ("title", "description")