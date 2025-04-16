# characters/models.py
from django.db import models
from django.contrib.auth.models import User

class CharacterSheet(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='charactersheets')
    name = models.CharField(max_length=100)
    character_class = models.CharField(max_length=100)
    race = models.CharField(max_length=100)
    level = models.IntegerField(default=1)
    # Use JSONField to store additional attributes (requires Django 3.1+)
    attributes = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
