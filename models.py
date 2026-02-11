
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):

    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]

    CATEGORY_CHOICES = [
        ('daily', 'Daily Work'),
        ('reading', 'Reading'),
        ('writing', 'Writing'),
        ('hobbies', 'Hobbies'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='daily')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['priority', 'deadline', '-created_at']
