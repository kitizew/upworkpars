from django.db import models


class Vacancy(models.Model):
    external_id = models.CharField(max_length=100, unique=True)  # ciphertext, напр. ~0221...
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    url = models.URLField(max_length=1000)
    budget = models.CharField(max_length=100, blank=True)
    job_type = models.IntegerField(null=True, blank=True)  # сире поле "type" з Upwork
    duration = models.CharField(max_length=100, blank=True)
    engagement = models.CharField(max_length=100, blank=True)
    tier = models.CharField(max_length=50, blank=True)
    proposals_tier = models.CharField(max_length=50, blank=True)
    skills = models.JSONField(default=list, blank=True)
    client_country = models.CharField(max_length=100, blank=True)
    client_total_spent = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    client_payment_status = models.IntegerField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-published_at"]

    def __str__(self):
        return self.title