import subprocess
from pathlib import Path

from rich.console import Console

console = Console()


def run_git(
    args: list[str],
    repo_root_path: Path | None = None,
    capture_output: bool = False,
    silent: bool = False,
) -> str | bool:
    """
    Выполняет команду Git с обработкой ошибок и опциональным выводом.

    Args:
        args (list[str]): Аргументы git-команды, например `["add", "."]`.
        repo_root_path (Path | None): Путь к корню репозитория. По умолчанию
            — текущая директория.
        capture_output (bool): Если True — возвращает stdout, иначе True/False
            по результату выполнения.
        silent (bool): Если True — подавляет вывод в консоль.

    Returns:
        str | bool: Стандартный вывод команды, если capture_output=True,
        иначе True/False в зависимости от успешности выполнения команды.
    """
    cwd = repo_root_path or Path(__file__).resolve().parent

    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            check=True,
            text=True,
            capture_output=capture_output,
        )
        if capture_output:
            return result.stdout
        if not silent and result.stdout:
            console.print(result.stdout.strip())
        return True
    except subprocess.CalledProcessError as e:
        if not silent:
            console.print(
                f"[red]Ошибка при выполнении git {' '.join(args)}[/red]"
            )
            if e.stderr:
                console.print(e.stderr.strip())
        return False


def repo_is_clean(repo_root_path: Path | None = None) -> bool:
    """
    Проверяет, есть ли незакоммиченные изменения в репозитории.

    Args:
        repo_root_path (Path | None): Путь к корню репозитория.
            Если не задан — используется текущая директория.

    Returns:
        bool: True, если в репозитории нет изменений, иначе False.
    """
    cwd = repo_root_path or Path(__file__).resolve().parent
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return len(result.stdout.strip()) == 0
