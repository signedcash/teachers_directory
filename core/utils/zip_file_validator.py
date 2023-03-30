import os
import zipfile
import io
from PIL import Image


def validate_zip_file(zip_file):
    """
    Validate the contents of a ZIP file containing profile images.

    This function checks if the ZIP file exists, is not empty, and if all files in it are valid
    images that can be opened with PIL.Image.

    Args:
        zip_file (InMemoryUploadedFile): ZIP file with profile images.

    Returns:
        bool: True if the ZIP file is valid, raises a ValueError with a detailed message if not.

    Raises:
        ValueError: If the ZIP file is missing, empty, or contains invalid image files.
    """

    try:
        with zipfile.ZipFile(zip_file) as f:
            file_names = f.namelist()
            if not file_names:
                raise ValueError('ZIP file validation failed with the following errors:\nZIP file is empty')

            # check for valid image files
            errors = []
            for file_name in file_names:
                with f.open(file_name) as image_file:
                    try:
                        with Image.open(io.BytesIO(image_file.read())) as img:
                            pass
                    except (OSError, IOError):
                        errors.append((file_name, 'Invalid image file'))

            if errors:
                error_messages = [f"File '{name}': {msg}" for name, msg in errors]
                error_msg = "ZIP file validation failed with the following errors:\n" + "\n".join(error_messages)
                raise ValueError(error_msg)

            # If there are no errors, return True
            return True
            
    except (zipfile.BadZipFile, IOError, OSError) as e:
        raise ValueError(f"Error opening the ZIP file: {e}")
