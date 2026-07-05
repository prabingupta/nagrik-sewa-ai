from django.db import models


class Service(models.Model):
    """Represents a government service (e.g. Passport, Citizenship, License)."""

    name = models.CharField(max_length=200)
    name_nepali = models.CharField(max_length=200, blank=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_popular = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


from django.contrib.auth.models import User


class Favorite(models.Model):
    """A service a user has bookmarked."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "service")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} → {self.service.name}"


class Query(models.Model):
    """Stores each user query and the AI-generated response for history/logging."""

    question = models.TextField()
    service = models.ForeignKey(
        Service, on_delete=models.SET_NULL, null=True, blank=True, related_name="queries"
    )
    answer_json = models.JSONField(blank=True, null=True)
    language = models.CharField(
        max_length=10,
        choices=[("en", "English"), ("ne", "Nepali")],
        default="en",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Queries"

    def __str__(self):
        return f"{self.question[:50]} ({self.language})"