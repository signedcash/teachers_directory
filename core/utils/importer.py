import zipfile
import pandas as pd

from django.core.files import File
from io import BytesIO
from core.models import Subject, Teacher


def import_teachers_from_csv_and_zip(csv_data, zip_file):
    """
    Import teachers and their profile pictures from a CSV file and a zip file.

    Args:
        csv_data (DataFrame): Dataframe with teacher data.
        zip_file (InMemoryUploadedFile): Zip file with profile pictures.
    """
    with zipfile.ZipFile(zip_file, 'r') as zip_ref:
        for _, row in csv_data.iterrows():
            teacher, created = Teacher.objects.get_or_create(
                email_address=row['email_address'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'phone_number': row['phone_number'],
                    'room_number': row['room_number'],
                }
            )

            if not created:
                teacher.first_name = row['first_name']
                teacher.last_name = row['last_name']
                teacher.phone_number = row['phone_number']
                teacher.room_number = row['room_number']

            if pd.isna(row['profile_picture']):
                teacher.profile_picture = File(None)
            else:
                try:
                    with zip_ref.open(row['profile_picture']) as img_file:
                        image_data = BytesIO(img_file.read())
                        teacher.profile_picture.save(
                            row['profile_picture'],
                            File(image_data)
                        )
                except KeyError:
                    pass

            subjects_list = row['subjects_taught'].split(",")
            for subject_name in subjects_list:
                subject_name = subject_name.strip().title()
                subject, _ = Subject.objects.get_or_create(name=subject_name)
                teacher.subjects_taught.add(subject)

            teacher.save()


def import_teachers_from_csv(csv_data):
    """
    Import teachers from a CSV file.

    Args:
        csv_data (DataFrame): Dataframe with teacher data.
    """
    for _, row in csv_data.iterrows():
        teacher, created = Teacher.objects.get_or_create(
            email_address=row['email_address'],
            defaults={
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'phone_number': row['phone_number'],
                'room_number': row['room_number'],
            }
        )

        if not created:
            teacher.first_name = row['first_name']
            teacher.last_name = row['last_name']
            teacher.phone_number = row['phone_number']
            teacher.room_number = row['room_number']

        if pd.isna(row['profile_picture']):
            teacher.profile_picture = File(None)

        subjects_list = row['subjects_taught'].split(",")
        for subject_name in subjects_list:
            subject_name = subject_name.strip().title()
            subject, _ = Subject.objects.get_or_create(name=subject_name)
            teacher.subjects_taught.add(subject)

        teacher.save()
