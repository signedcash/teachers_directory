import re
import pandas as pd
import numpy as np


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


def check_email_format_and_uniqueness(df):
    """
    Checks for valid and unique email addresses.

    Args:
        df (pd.DataFrame): DataFrame containing the data.

    Returns:
        list: List of tuples containing the row index, column name, and error message.
    """
    errors = []
    email_pattern = re.compile(r"[^@]+@[^@]+\.[^@]+")
    for index, email in df['email_address'].items():
        if not bool(email_pattern.match(email)):
            errors.append((index, 'email_address', "Invalid email address"))
        if not df['email_address'].is_unique:
            errors.append((index, 'email_address', "Duplicate email address"))
    return errors


def check_phone_number_format(df):
    """
    Checks for valid phone number format.

    Args:
        df (pd.DataFrame): DataFrame containing the data.

    Returns:
        list: List of tuples containing the row index, column name, and error message.
    """
    errors = []
    phone_number_pattern = re.compile(r'\+\d{1,3}-\d{3}-\d{3}-\d{3}')
    for index, phone_number in df['phone_number'].items():
        if not bool(phone_number_pattern.match(phone_number)):
            errors.append((index, 'phone_number', "Invalid phone number"))
    return errors


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


def validate_csv_file(csv_file):
    """
    Validate the contents of a CSV file containing teacher data.

    This function checks if the required columns are present and if the data in the columns
    is valid. It validates the first_name, last_name, email, phone_number, room_number and
    subjects_taught columns. The profile_picture column is optional.

    Args:
        csv_file (InMemoryUploadedFile): CSV file with teacher data.

    Returns:
        bool: True if the CSV file is valid, raises a ValueError with a detailed message if not.

    Raises:
        ValueError: If the CSV file is missing required columns, has empty fields,
                    or contains invalid data in any of the columns.
    """
    try:
        df = pd.read_csv(csv_file)
    except (FileNotFoundError, IOError) as e:
        raise ValueError(f"Error opening the CSV file: {e}")

    # Convert column names to lower case and join words with an underscore
    df.columns = df.columns.str.lower().str.replace(' ', '_')

    # Check if the required columns are present
    required_columns = {'first_name', 'last_name', 
                        'email_address', 'phone_number', 
                        'room_number', 'profile_picture', 
                        'subjects_taught'}
    if not required_columns.issubset(df.columns):
        raise ValueError('CSV file is missing required columns.')

    # Replace all empty strings and strings consisting only of whitespace with NaN
    df = df.replace(r'^\s*$', np.nan, regex=True)

    # Remove rows where all variables are NaN
    df = df.dropna(how='all')
    errors = []  # List of errors

    # Check for empty fields, except for 'profile_picture'
    required_fields = required_columns - {'profile_picture'}
    errors.extend(check_empty_fields(df, required_fields))

    # Check for unique and valid email addresses
    errors.extend(check_email_format_and_uniqueness(df))

    # Check for valid phone number format
    errors.extend(check_phone_number_format(df))

    # Check that the number of elements in 'subjects_taught' is not greater than 5
    errors.extend(check_subjects_taught(df))

    # If there are any errors, raise a ValueError with a detailed message
    if errors:
        error_messages = [f"Row {index}, Column '{col}': {msg}" for index, col, msg in errors]
        error_msg = "CSV validation failed with the following errors:\n" + "\n".join(error_messages)
        raise ValueError(error_msg)
    
    # If there are no errors, return prepared file
    return df
