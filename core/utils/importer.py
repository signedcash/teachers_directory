import pandas as pd
import zipfile
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
        for index, row in csv_data.iterrows():
            teacher = Teacher(
                first_name=row['first_name'],
                last_name=row['last_name'],
                email_address=row['email_address'],
                phone_number=row['phone_number'],
                room_number=row['room_number']
            )

            teacher.save()


            profile_picture_filename = row['profile_picture']
            if profile_picture_filename:
                try:
                    with zip_ref.open(profile_picture_filename) as img_file:
                        image_data = BytesIO(img_file.read())
                        teacher.profile_picture.save(profile_picture_filename, File(image_data))
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
    for index, row in csv_data.iterrows():
        teacher = Teacher(
            first_name=row['first_name'],
            last_name=row['last_name'],
            email_address=row['email_address'],
            phone_number=row['phone_number'],
            room_number=row['room_number']
        )

        teacher.save()

        subjects_list = row['subjects_taught'].split(",")
        for subject_name in subjects_list:
            subject_name = subject_name.strip().title()
            subject, _ = Subject.objects.get_or_create(name=subject_name)
            teacher.subjects_taught.add(subject)

        teacher.save()
