import os

SUPPORTED_IMAGE_EXTENSIONS: set = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
}
LENGTH_UNIX_TIME: int = 10


def is_image(filepath: str) -> bool:
    """Проверяет, является ли файл изображением по расширению."""
    _, file_extension = os.path.splitext(filepath)
    return file_extension.lower() in SUPPORTED_IMAGE_EXTENSIONS


def is_already_renamed(filename: str) -> bool:
    """Проверяет, соответствует ли имя файла шаблону <timestamp>.<ext>."""
    try:
        name, ext = os.path.splitext(filename)
        if (
            name.isdigit()
            and len(name) == LENGTH_UNIX_TIME
            and ext.lower() in SUPPORTED_IMAGE_EXTENSIONS
        ):
            return True
        return False
    except (ValueError, IndexError):
        return False


def generate_new_filename(filename: str, timestamp: int) -> str:
    """Создаёт имя файла вида <timestamp>.<ext>."""
    _, ext = os.path.splitext(filename)
    return f"{timestamp}{ext.lower()}"
