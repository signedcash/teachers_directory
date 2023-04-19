from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from core.validators.csv_file_validator import CSVFileValidator
from core.validators.zip_file_validator import ZipFileValidator


class RegisterForm(UserCreationForm):
    """
    A form for user registration that extends the built-in UserCreationForm.

    Inherits fields: 'username', 'password1', and 'password2'.
    """
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']


class TeachersImportForm(forms.Form):
    """
    A form for importing teacher data from CSV and profile pictures from ZIP.

    Fields: 'csv_file' and 'zip_file'.
    """
    csv_file = forms.FileField(
        label='Teacher Data (CSV)', 
        validators=[
            FileExtensionValidator(allowed_extensions=['csv']),
            CSVFileValidator(),
        ]
    )

    zip_file = forms.FileField(
        label='Profile pictures (ZIP):', 
        required=False, 
        validators=[
            FileExtensionValidator(allowed_extensions=['zip']), 
            ZipFileValidator(),
        ]
    )