from django import forms
from .models import Habit, User

class HabitLogForm(forms.Form):
    note = forms.CharField(label="Note for today (optional)", required=False)
    
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
        self.fields["users"].queryset = user.friends.all()
        self.fields["users"].initial = [user]

