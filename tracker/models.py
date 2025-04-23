from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class User(AbstractUser):
    friends = models.ManyToManyField("self", symmetrical=True, blank=True)
    
class Category(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

class Habit(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    description = models.TextField(blank=True)
    users = models.ManyToManyField(User, related_name="shared_habits")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="habits_owned", null=True, blank=True)
    target_minutes = models.PositiveIntegerField(default=30)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='habits')

    def __str__(self):
        return self.name

class HabitLog(models.Model):
    habit = models.ForeignKey(Habit, on_delete=models.CASCADE, related_name="logs")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    minutes_done = models.PositiveIntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ("habit", "user", "date")
    
    def __str__(self):
        return f"{self.user.username} - {self.habit.name} on {self.date}"

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name="friend_requests_sent", on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name="friend_requests_received", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def accept(self):
        self.to_user.friends.add(self.from_user)
        self.from_user.friends.add(self.to_user)
        self.delete()

    def decline(self):
        self.delete()