from datetime import datetime
from pathlib import Path

import questionary
from rich.console import Console

from apps.gitops.src.utils import run_git, repo_is_clean

console = Console()


def git_push(repo_root_path: Path | None = None) -> None:
    """
    Выполняет коммит и отправку изменений в удалённый репозиторий.

    Алгоритм:
      1. Проверяет наличие незакоммиченных изменений.
      2. Показывает краткий список изменённых файлов.
      3. Предлагает создать автоматический коммит (UTC-время в сообщении).
      4. Проверяет наличие неотправленных коммитов.
      5. Если они есть — предлагает выполнить git push.
      6. Сообщает об успехе или ошибке операции.

    Args:
        repo_root_path (Path | None): Путь к корню репозитория.
    """
    console.print(
        "Проверка состояния репозитория...", style="bold cyan"
    )

    # --- Проверяем наличие незакоммиченных изменений ---
    if not repo_is_clean(repo_root_path=repo_root_path):
        console.print(
            "\nОбнаружены незакоммиченные изменения:", style="yellow"
        )
        diff_output = run_git(
            ["status", "--short"],
            repo_root_path=repo_root_path,
            capture_output=True,
        )

        if diff_output:
            console.print(f"[dim]{diff_output}[/dim]")
        else:
            console.print(
                "Не удалось получить список изменений.\n", style="red"
            )

        if questionary.confirm("Составить автоматический коммит?").ask():
            dt = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            console.print("Создание коммита...", style="cyan")
            run_git(["add", "."], repo_root_path=repo_root_path)
            run_git(
                ["commit", "-m", f"auto: {dt}"],
                repo_root_path=repo_root_path,
            )
            console.print(" ✔ Коммит создан", style="green")
        else:
            console.print(" ✘ Коммит отменён", style="yellow")
    else:
        console.print(" ○ Нет изменений для коммита", style="green")

    ahead_check = run_git(
        ["rev-list", "@{u}..HEAD", "--count"],
        repo_root_path=repo_root_path,
        capture_output=True,
    )

    if ahead_check is None:
        console.print(
            " ⚠ Не удалось определить состояние ветки относительно origin.",
            style="yellow"
        )
        return

    try:
        ahead_count = int(ahead_check.strip())
    except ValueError:
        ahead_count = 0

    if ahead_count == 0:
        console.print(" ○ Нет новых коммитов для отправки.", style="green")
        return

    console.print(f"Неотправленных коммитов: {ahead_count}", style="cyan")
    if not questionary.confirm("Отправить изменения в репозиторий?").ask():
        console.print(" ✘ Push отменён", style="yellow")
        return

    console.print("Сохранение и отправка изменений...", style="cyan")
    if not run_git(["push"], repo_root_path=repo_root_path):
        console.print(
            "Не удалось выполнить push.",
            "Возможная причина: удалённый репозиторий был обновлён.",
            style="red"
        )
        console.print("Попробуйте сначала выполнить pull.", style="yellow")
        return

    console.print(" ✔ Изменения успешно отправлены", style="green")


def git_pull(repo_root_path: Path | None = None) -> None:
    """
    Выполняет git pull при наличии обновлений в удалённом репозитории.

    Алгоритм:
      1. Выполняет `git fetch` и сравнивает количество коммитов между
        локальной и удалённой ветками.
      2. Сообщает пользователю, если репозиторий неактуален.
      3. Предлагает выполнить обновление (`git pull --ff-only`).
      4. Выводит результат операции.

    Args:
        repo_root_path (Path | None): Путь к корню репозитория.
    """
    console.print("Проверка обновлений...", style="bold cyan")
    run_git(
        ["fetch", "--quiet"],
        repo_root_path=repo_root_path,
    )
    updates_count_str = run_git(
        ["rev-list", "@..@{u}", "--count"],
        repo_root_path=repo_root_path,
        capture_output=True,
        silent=True,
    )

    if not updates_count_str:
        console.print(
            " ⚠ Upstream для текущей ветки не задан.",
            "Невозможно проверить актуальность.",
            style="yellow"
        )
        return

    try:
        updates_count = int(updates_count_str.strip())
    except ValueError:
        console.print(
            "Ошибка: Не удалось распознать счётчик коммитов от Git.",
            style="red"
        )
        return

    if updates_count == 0:
        console.print(" ✔ Репозиторий уже актуален", style="green")
        return

    console.print(
        "Репозиторий отстаёт от удалённой ветки на",
        f"[red]{updates_count}[/red] коммитов.",
        style="yellow"
    )

    if not questionary.confirm(
        "Обновить локальный репозиторий (git pull)?"
    ).ask():
        console.print(" ✘ Обновление отменено", style="yellow")
        return

    result = run_git(
        ["pull", "--ff-only"],
        repo_root_path=repo_root_path,
        capture_output=True,
    )
    if result:
        console.print(" ✔ Репозиторий обновлён", style="green")
        return

    console.print("Не удалось выполнить pull.", style="red")


def main():
    """
    Отображает интерактивное меню для выбора Git-действий.

    Доступные опции:
      - Push (отправка изменений)
      - Pull (обновление репозитория)
      - Выход
    """
    action = questionary.select(
        "Выберите действие:",
        choices=[
            "Push (отправить изменения)",
            "Pull (обновить репозиторий)",
            "Выход"
        ]
    ).ask()

    if action.startswith("Push"):
        git_push()
    elif action.startswith("Pull"):
        git_pull()
    else:
        console.print("Выход", style="yellow")
