from django import forms
from django.contrib.auth.models import User
from .models import Author, Quote

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match")

        return cleaned_data


class SearchForm(forms.Form):
    query = forms.CharField(label='Search by Tag', max_length=100)


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['fullname', 'born_date', 'born_location', 'description']

class QuoteForm(forms.ModelForm):
    class Meta:
        model = Quote
        fields = ['text', 'author']

#class CreateDatabaseForm(forms.Form):
#    db_name = forms.CharField(label='Database Name', max_length=100)    