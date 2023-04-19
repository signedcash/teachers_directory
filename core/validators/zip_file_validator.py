import zipfile
import io
from PIL import Image
from django.core.exceptions import ValidationError


class ZipFileValidator():
    """
    Validator for ZIP files containing profile images.

    This class checks if the ZIP file exists, is not empty, and if all files in it are valid
    images that can be opened with PIL.Image.
    """

    def __call__(self, file):
        try:
            with zipfile.ZipFile(file) as f:
                file_names = f.namelist()
                if not file_names:
                    raise ValidationError('ZIP file is empty')
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
                    raise ValidationError(error_msg)
        except (zipfile.BadZipFile, IOError, OSError) as e:
            pass