from django.core.exceptions import ValidationError
from django.conf import settings
import os


def validate_file_size(file):
    """
    Validate that the uploaded file does not exceed the maximum allowed size.
    """
    max_size = getattr(settings, 'MAX_FILE_SIZE', 5 * 1024 * 1024)  # Default 5MB
    if file.size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB. Your file is {file.size / (1024 * 1024):.2f}MB.')


def validate_file_extension(file):
    """
    Validate that the uploaded file has an allowed extension.
    """
    allowed_extensions = getattr(settings, 'ALLOWED_FILE_EXTENSIONS', 
                                  ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'png', 'jpg', 'jpeg'])
    
    ext = os.path.splitext(file.name)[1][1:].lower()  # Get extension without dot
    
    if ext not in allowed_extensions:
        raise ValidationError(
            f'File type ".{ext}" is not allowed. Allowed types: {", ".join(allowed_extensions)}'
        )
