import os

SUPPORTED_IMAGE_EXTENSIONS: set = {
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
}
LENGTH_UNIX_TIME: int = 10


def is_image(filepath: str) -> bool:
    """
    Проверяет, является ли файл изображением по его расширению.

    Args:
        filepath (str): Полный путь к файлу.

    Returns:
        bool: True, если расширение поддерживается
            (`SUPPORTED_IMAGE_EXTENSIONS`), иначе False.
    """
    _, file_extension = os.path.splitext(filepath)
    return file_extension.lower() in SUPPORTED_IMAGE_EXTENSIONS


def is_already_renamed(filename: str) -> bool:
    """
    Проверяет, соответствует ли имя файла шаблону `<timestamp>.<ext>`.

    Шаблон считается корректным, если:
      - имя состоит только из цифр (`isdigit()`),
      - длина имени равна `LENGTH_UNIX_TIME`,
      - расширение поддерживается (`SUPPORTED_IMAGE_EXTENSIONS`).

    Args:
        filename (str): Имя файла без пути.

    Returns:
        bool: True, если файл уже имеет формат `<timestamp>.<ext>`,
            иначе False.
    """
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
    """
    Генерирует новое имя файла в формате `<timestamp>.<ext>`.

    Args:
        filename (str): Оригинальное имя файла (используется для
            сохранения расширения).
        timestamp (int): Временная метка Unix (секунды с 1970 года).

    Returns:
        str: Новое имя файла, приведённое к нижнему регистру расширения.
    """
    _, ext = os.path.splitext(filename)
    return f"{timestamp}{ext.lower()}"
