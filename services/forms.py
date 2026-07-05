from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class NagarikRegistrationForm(UserCreationForm):
    first_name = forms.CharField(label="Full Name", max_length=150, required=True)
    age = forms.IntegerField(label="Age", min_value=1, max_value=120, required=True)

    class Meta:
        model = User
        fields = ["username", "first_name", "age", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        if commit:
            user.save()
            from .models import UserProfile
            UserProfile.objects.create(user=user, age=self.cleaned_data["age"])
        return user
