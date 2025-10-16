from rich.console import Console
import questionary

from apps.menu.src.utils import is_submodule, get_cuberbug_walls_path
from apps.gitops.src.core import git_pull, git_push
from apps.renamer.src.core import rename_files

console = Console()
title_text = """
::::::::::::::::::::::::::::::::::::::
:::::::::::: [bold cyan]Главное меню[/bold cyan] ::::::::::::
:::::::::::::::::::::::::::: v2.0.0 ::

"""


def main_menu():
    console.print(title_text)

    submodule_mode = is_submodule()

    while True:
        choice = questionary.select(
            "Выберите действие:",
            choices=[
                "Сохранить (git push)",
                "Обновить (git pull)",
                "Renamer (переименование изображений)",
                "Выход"
            ]
        ).ask()

        if choice == "Сохранить (git push)":
            git_push()
        elif choice == "Обновить (git pull)":
            git_pull()
        elif choice == "Renamer (переименование изображений)":
            renamer_menu(submodule_mode)
        elif choice == "Выход" or choice is None:
            console.print("\n[bold yellow]Выход из программы...[/bold yellow]")
            break


def renamer_menu(is_submodule_mode: bool):
    console.print("\n[bold cyan]Renamer — Подменю[/bold cyan]\n")

    choices = []
    if is_submodule_mode:
        choices.extend([
            "Переименовать изображения в cuberbug_walls/ (сухой запуск)",
            "Переименовать изображения в cuberbug_walls/",
        ])

    choices.append("Указать свой путь к директории для запуска")
    choices.append("Назад")

    while True:
        choice = questionary.select(
            "Выберите действие:", choices=choices
        ).ask()

        if choice == "Назад" or choice is None:
            break
        elif "cuberbug_walls/" in choice:
            dry_run = "сухой" in choice
            walls_path = get_cuberbug_walls_path()
            if walls_path:
                rename_files(walls_path, dry_run=dry_run)
        elif "Указать свой путь" in choice:
            path = questionary.path("Укажите путь к директории:").ask()
            if not path:
                console.print("[red]Отменено[/red]")
                continue
            dry_run = questionary.confirm(
                "Выполнить сухой запуск (без переименования)?"
            ).ask()
            rename_files(path, dry_run=dry_run)
