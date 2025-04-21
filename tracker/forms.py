from django import forms
from .models import Habit

class HabitLogForm(forms.Form):
    note = forms.CharField(label="Note for today (optional)", required=False)
    
class HabitForm(forms.ModelForm):
    class Meta:
        model = Habit
        fields = ['name', 'category', 'users']
        widgets = {
            "users": forms.CheckboxSelectMultiple
        }