from pathlib import Path

# Наборы файлов-маркеров для определения типа директории
MARKERS_ROOT: set[str] = {".gitignore", "setup.cfg", "LICENSE"}
MARKERS_SUBMODULE: set[str] = {".gitmodules"}
MARKERS_CUBERBUG_WALLS_ROOT: set[str] = {".gitmodules", "manager.sh"}

NAME_WALLPAPERS_DIR: str = "wallpapers"


def find_path_to_marker(
    markers: set[str], start: Path | None = None
) -> Path | None:
    """
    Рекурсивно ищет директорию, содержащую хотя бы один из указанных
    файлов-маркеров.

    Args:
        markers (set[str]): Имена файлов или директорий, наличие которых
            указывает на нужную директорию.
        start (Path | None): Точка начала поиска. По умолчанию — директория
            текущего файла.

    Returns:
        Path | None: Путь к найденной директории или None, если маркеры
            не обнаружены.
    """
    if start is None:
        start = Path(__file__).resolve()
    current = start if start.is_dir() else start.parent

    # Поднимаемся до корня файловой системы
    while True:
        for marker in markers:
            if (current / marker).exists():
                return current
        if current.parent == current:  # достигли корня FS
            break
        current = current.parent
    return None


def get_cuberbug_walls_path(start: Path | None = None) -> Path | None:
    """
    Определяет путь к директории `wallpapers` в корне проекта `cuberbug_walls`.

    Args:
        start (Path | None): Путь, откуда начать поиск. По умолчанию — текущая
            директория.

    Returns:
        Path | None: Путь к директории `wallpapers`, если найден, иначе None.
    """
    cuberbug_walls_root = find_path_to_marker(
        MARKERS_CUBERBUG_WALLS_ROOT, start
    )
    if not cuberbug_walls_root:
        return None
    candidate = cuberbug_walls_root / NAME_WALLPAPERS_DIR
    return candidate if candidate.exists() else None


def is_submodule() -> bool:
    """
    Определяет, является ли текущий репозиторий сабмодулем другого проекта.

    Алгоритм:
      1. Находит корень текущего репозитория по маркерам.
      2. Проверяет наличие `.gitmodules` в родительской директории.
      3. Читает `.gitmodules` и ищет в нём путь к текущему репозиторию.

    Returns:
        bool: True, если текущий репозиторий зарегистрирован как сабмодуль,
            иначе False.
    """
    root = find_path_to_marker(MARKERS_ROOT)
    if not root:
        return False

    parent = root.parent
    gitmodules = parent / ".gitmodules"

    if not gitmodules.exists():
        return False

    try:
        content = gitmodules.read_text(encoding="utf-8")
    except OSError:
        return False

    # Проверяем, содержится ли путь к сабмодулю в .gitmodules
    return str(root.relative_to(parent)) in content


def get_root_path(is_submodule: bool = None) -> Path | None:
    """
    Определяет корневую директорию текущего репозитория.

    Args:
        is_submodule (bool | None): Если True — поиск выполняется по маркерам
            сабмодуля. Если False или None — по маркерам обычного репозитория.

    Returns:
        Path | None: Путь к корню репозитория, если найден, иначе None.
    """
    markers = MARKERS_ROOT

    if is_submodule:
        markers = MARKERS_SUBMODULE

    repo_root = find_path_to_marker(markers)
    return repo_root if repo_root and repo_root.exists() else None
