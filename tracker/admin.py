from django.contrib import admin
from .models import Category, Habit, HabitLog

admin.site.register(Category)
admin.site.register(Habit)
admin.site.register(HabitLog)