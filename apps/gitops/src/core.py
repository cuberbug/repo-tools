import questionary
from rich.console import Console

from apps.gitops.src.utils import run_git, repo_is_clean

console = Console()


def git_push():
    """Отправка изменений в удалённый репозиторий"""
    console.print("[bold cyan]Проверка состояния репозитория...[/bold cyan]")

    if repo_is_clean():
        console.print("[green]Нет изменений для коммита[/green]")
    else:
        if questionary.confirm("Составить автоматический коммит?").ask():
            from datetime import datetime
            dt = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            console.print("[cyan]Создание коммита...[/cyan]")
            run_git(["add", "."])
            run_git(["commit", "-m", f"Auto: {dt}"])
            console.print("[green]Коммит создан[/green]")
        else:
            console.print("[yellow]Отмена[/yellow]")

    if questionary.confirm("Отправить изменения в репозиторий?").ask():
        console.print("[cyan]Сохранение и отправка изменений...[/cyan]")
        if not run_git(["push"]):
            console.print(
                "[red]Не удалось выполнить push. Возможная причина: "
                "удалённый репозиторий был обновлён.[/red]"
            )
            console.print(
                "[yellow]Попробуйте сначала выполнить pull.[/yellow]"
            )
        else:
            console.print("[green]Изменения успешно отправлены[/green]")
    else:
        console.print("[yellow]Отмена[/yellow]")


def git_pull():
    console.print("[bold cyan]Проверка обновлений...[/bold cyan]")
    run_git(["fetch", "--quiet"])
    updates_count_str = run_git(
        ["rev-list", "--count", "@..@{u}"],
        capture_output=True,
        silent=True
    )

    if not updates_count_str:
        console.print(
            "[yellow]Предупреждение: Upstream для текущей ветки не задан. "
            "Невозможно проверить актуальность.[/yellow]"
        )
        return

    try:
        updates_count = int(updates_count_str.strip())
    except ValueError:
        console.print(
            "[red]Ошибка: Не удалось распознать счётчик коммитов от Git.[/red]"
        )
        return

    if updates_count == 0:
        console.print("[green]Репозиторий уже актуален[/green]")
        return
    else:
        console.print(
            "[yellow]Репозиторий отстаёт от удалённой ветки на "
            f"{updates_count} коммитов.[/yellow]"
        )

    if questionary.confirm("Обновить локальный репозиторий (git pull)?").ask():
        result = run_git(["pull", "--ff-only"])
        if result:
            console.print("[green]Репозиторий обновлён[/green]")
        else:
            console.print("[red]Не удалось выполнить pull.[/red]")
    else:
        console.print("[yellow]Отмена[/yellow]")


def main():
    """Интерактивный выбор действия"""
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
        console.print("[yellow]Выход[/yellow]")
