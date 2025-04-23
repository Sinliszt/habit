from django import forms
from .models import Habit, User, HabitLog

class HabitLogForm(forms.ModelForm):
    class Meta:
        model = HabitLog
        fields = ["minutes_done", "note"]  

        widgets = {
            "note": forms.Textarea(attrs ={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Write a quick note (optional)",
            }),
            "minutes_done": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 0,
                "max": 180,
            })
        }  
class HabitForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )
    class Meta:
        model = Habit
        fields = ['name', 'category', 'users', 'target_minutes']

        widgets = {
            "target_minutes": forms.NumberInput(attrs={
                "class": "form-control",
                "min": 1,
                "max": 180,
                "placeholder": "Enter your daily target(in mins)"
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["users"].required = False
        self.fields["users"].queryset = user.friends.all()
        self.fields["users"].initial = [user]

