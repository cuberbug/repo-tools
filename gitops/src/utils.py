import subprocess

from rich.console import Console

console = Console()


def run_git(args, capture_output=False, silent=False):
    """
    Выполняет git-команду с обработкой ошибок.
    Возвращает stdout (если capture_output=True) или True/False по результату.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            check=True,
            text=True,
            capture_output=capture_output
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


def repo_is_clean():
    """
    Проверяет, есть ли незакоммиченные изменения.
    Возвращает True, если репозиторий чист.
    """
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True
    )
    return len(result.stdout.strip()) == 0
