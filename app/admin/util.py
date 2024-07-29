import os
import os
import imghdr
from werkzeug.utils import escape, secure_filename

from flask import current_app

def sanitize_filename(filename):
    filename = escape(secure_filename(filename))
    filename = filename.replace("(", "").replace(")", "") # for Markdown parsing
    return filename


def upload_images(images, images_path) -> str:
    try:
        for image in images:
            if image.filename == "": # this happens when no image is submitted
                continue

            filename = sanitize_filename(image.filename)
            if filename == "":
                return "Image name was reduced to atoms by sanitization."

            file_ext = os.path.splitext(filename)[1]
            if file_ext == ".jpg": # since `validate_image()` (`imghdr.what()`) returns everything as `jpeg`
                file_ext = ".jpeg"
            invalid = \
                    file_ext not in current_app.config["IMAGE_UPLOAD_EXTENSIONS"] \
                    or (file_ext in current_app.config["IMAGE_UPLOAD_EXTENSIONS_CAN_VALIDATE"] \
                    and file_ext != validate_image(image.stream)) # imghdr can't check SVG; trustable since admin-only?
            if invalid:
                return "Invalid image. If it's another heic or webp im gonna lose my mind i swear to god theyre so annoying i hat"

            path = os.path.join(images_path, filename)
            os.makedirs(images_path, exist_ok=True)               # mkdir -p if not exist
            image.save(path)                                      # replaces image if it's already there
    except Exception as e:
        return f"Image upload exception: {str(e)}"
    
    return None


def validate_image(image):
    header = image.read(512)
    image.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return f".{format}"
