import re
import pandas as pd
import numpy as np

from django.forms import ValidationError
from pandas.errors import ParserError

class CSVFileValidator():
    """
    Class that validates a CSV file containing teacher data according to certain requirements. 
    The CSV file must contain the following columns: 'first_name', 'last_name', 'email_address', 
    'phone_number', 'room_number', and 'subjects_taught'. The 'email_address' and 'phone_number' 
    columns must contain valid email addresses and phone numbers respectively. The 'subjects_taught' 
    column must not contain more than 5 elements. The class also checks for missing values in required 
    fields, uniqueness and validity of email addresses, and the format of phone numbers.

    Attributes:
        REQUIRED_COLUMNS (set): Set of required column names.
        EMAIL_PATTERN (re.Pattern): Regular expression pattern for valid email addresses.
        PHONE_NUMBER_PATTERN (re.Pattern): Regular expression pattern for valid phone numbers.

    Raises:
        ValidationError: If the CSV file does not meet the requirements.
    """

    REQUIRED_COLUMNS = {
        'first_name', 'last_name', 'email_address', 
        'phone_number', 'room_number', 'subjects_taught'
    }
    EMAIL_PATTERN = re.compile(r"[^@]+@[^@]+\.[^@]+")
    PHONE_NUMBER_PATTERN = re.compile(r'\+\d{1,3}-\d{3}-\d{3}-\d{3}')

    def __call__(self, file):
        try:
            df = pd.read_csv(file)
        except (FileNotFoundError, IOError) as e:
            raise ValidationError(f"Error opening the CSV file: {e}")
        except ParserError as e:
            raise ValidationError(e)
        # Convert column names to lower case and join words with an underscore
        df.columns = df.columns.str.lower().str.replace(' ', '_')

        # Check if the required columns are present
        if not self.REQUIRED_COLUMNS.issubset(df.columns):
            raise ValidationError('CSV file is missing required columns.')

        # Replace all empty strings and strings consisting only of whitespace with NaN
        df = df.replace(r'^\s*$', np.nan, regex=True)

        # Remove rows where all variables are NaN
        df = df.dropna(how='all')

        errors = []  # List of errors

        # Check for empty fields, except for 'profile_picture'
        required_fields = self.REQUIRED_COLUMNS - {'profile_picture'}
        errors.extend(self.check_empty_fields(df, required_fields))

        # Check for unique and valid email addresses
        errors.extend(self.check_email_format_and_uniqueness(df))

        # Check for valid phone number format
        errors.extend(self.check_phone_number_format(df))

        # Check that the number of elements in 'subjects_taught' is not greater than 5
        errors.extend(self.check_subjects_taught(df))
        
        error_indexes = set([index for index, _, _ in errors])
        df.drop(error_indexes, inplace=True)
        df.to_csv("data_temp.csv", index=False)
        
        # If there are any errors, raise a ValueError with a detailed message
        if errors:
            error_messages = [f"Row {index}, Column '{col}': {msg}" for index, col, msg in errors]
            raise ValidationError(error_messages)


    @staticmethod
    def check_empty_fields(df, required_fields):
        """
        Checks for empty values in the specified fields.

        Args:
            df (pd.DataFrame): DataFrame containing the data.
            required_fields (set): Set of required field names.

        Returns:
            list: List of tuples containing the row index, column name, and error message.
        """
        errors = []
        for index, row in df[list(required_fields)].isnull().iterrows():
            for col, is_null in row.items():
                if is_null:
                    errors.append((index, col, "Field is empty"))
        return errors

    @staticmethod
    def check_email_format_and_uniqueness(df):
        """
        Checks for valid and unique email addresses.

        Args:
            df (pd.DataFrame): DataFrame containing the data.

        Returns:
            list: List of tuples containing the row index, column name, and error message.
        """
        errors = []
        for index, email in df['email_address'].items():
            if not bool(CSVFileValidator.EMAIL_PATTERN.match(email)):
                errors.append((index, 'email_address', "Invalid email address"))
            if not df['email_address'].is_unique:
                errors.append((index, 'email_address', "Duplicate email address"))
        return errors

    @staticmethod
    def check_phone_number_format(df):
        """
        Checks for valid phone number format.

        Args:
            df (pd.DataFrame): DataFrame containing the data.

        Returns:
            list: List of tuples containing the row index, column name, and error message.
        """
        errors = []
        for index, phone_number in df['phone_number'].items():
            if not bool(CSVFileValidator.PHONE_NUMBER_PATTERN.match(phone_number)):
                errors.append((index, 'phone_number', "Invalid phone number"))
        return errors

        
    @staticmethod
    def check_subjects_taught(df):
        """
        Checks for valid subjects taught format (no more than 5 subjects).

        Args:
            df (pd.DataFrame): DataFrame containing the data.

        Returns:
            list: List of tuples containing the row index, column name, and error message.
        """
        errors = []
        for index, subjects in df['subjects_taught'].items():
            if not pd.isna(subjects):
                if len(subjects.split(',')) > 5:
                    errors.append((index, 'subjects_taught', "More than 5 subjects"))
        return errors