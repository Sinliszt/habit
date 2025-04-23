from django import forms
from .models import Habit, User, HabitLog

class HabitLogForm(forms.Form):
    class Meta:
        model = HabitLog
        fields = ["minutes_done", "note"]    
class HabitForm(forms.ModelForm):
    users = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
    )
    class Meta:
        model = Habit
        fields = ['name', 'category', 'users']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields["users"].required = False
        self.fields["users"].queryset = user.friends.all()
        self.fields["users"].initial = [user]

