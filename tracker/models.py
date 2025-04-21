from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now

class Category(models.Model):
    name=models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Habit(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name="shared_habits")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='habits')

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("habit", "user", "date")
    
    def __str__(self):
        return f"{self.user.username} - {self.habit.name} on {self.date}"
