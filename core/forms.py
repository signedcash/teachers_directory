from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    """
    A form for user registration that extends the built-in UserCreationForm. 

    Inherits fields: 'username', 'password1', and 'password2'.
    """
    class Meta:
        model=User
        fields = ['username','password1','password2'] 


class LoginForm(forms.Form):
    """
    A form for user login.

    Fields: 'username' and 'password'.
    """
    username = forms.CharField(label='Username', 
                               max_length=100, 
                               widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label='Password', 
                               max_length=100, 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class ImportForm(forms.Form):
    """
    A form for importing teacher data from CSV and profile pictures from ZIP.

    Fields: 'csv_file' and 'zip_file'.
    """
    csv_file = forms.FileField(label='Teacher Data (CSV)')
    zip_file = forms.FileField(label='Profile pictures (ZIP):', required=False)
