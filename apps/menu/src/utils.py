from pathlib import Path

# Наборы файлов-маркеров для определения типа директории
MARKERS_ROOT: set[str] = {".gitignore", "setup.cfg", "LICENSE"}
MARKERS_SUBMODULE: set[str] = {".gitmodules"}
MARKERS_CUBERBUG_WALLS_ROOT: set[str] = {".gitmodules", "manager.sh"}

NAME_WALLPAPERS_DIR: str = "wallpapers"


def find_path_to_marker(
    markers: set[str], start: Path | None = None
) -> Path | None:
    """Ищет директорию по маркеру."""
    if start is None:
        start = Path(__file__).resolve()
    cur = start if start.is_dir() else start.parent

    # Поднимаемся до корня файловой системы
    while True:
        for marker in markers:
            if (cur / marker).exists():
                return cur
        if cur.parent == cur:  # достигли корня FS
            break
        cur = cur.parent
    return None


def get_root_path(start: Path | None = None) -> Path | None:
    """Определяет корень основного репозитория по набору маркеров."""
    repo_root = find_path_to_marker(MARKERS_ROOT, start)
    return repo_root if repo_root and repo_root.exists() else None


def get_cuberbug_walls_path(start: Path | None = None) -> Path | None:
    """Ищет путь к wallpapers в репозитории cuberbug_walls."""
    cuberbug_walls_root = find_path_to_marker(
        MARKERS_CUBERBUG_WALLS_ROOT, start
    )
    if not cuberbug_walls_root:
        return None
    candidate = cuberbug_walls_root / NAME_WALLPAPERS_DIR
    return candidate if candidate.exists() else None


def is_submodule() -> bool:
    """
    Проверяет, является ли текущий репозиторий сабмодулем другого проекта.

    Алгоритм:
      1. Находит корень текущего репозитория.
      2. Проверяет, есть ли в родительской директории файл .gitmodules.
      3. Если найден: читает и проверяет, упоминается ли путь к текущему репо.
    """
    root = get_root_path()
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
