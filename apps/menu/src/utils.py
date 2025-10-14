import os


def is_submodule() -> bool:
    """Проверяет, является ли текущий проект сабмодулем."""
    parent_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../..")
    )
    return os.path.isfile(os.path.join(parent_dir, ".gitmodules"))
