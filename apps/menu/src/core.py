from pathlib import Path

import questionary
from rich.console import Console

from apps.menu.src.utils import (
    is_submodule, get_cuberbug_walls_path, get_root_path
)
from apps.gitops.src.core import git_pull, git_push
from apps.renamer.src.core import rename_files

console = Console()
title_text = """
::::::::::::::::::::::::::::::::::::::
:::::::::::: [bold cyan]Главное меню[/bold cyan] ::::::::::::
:::::::::::::::::::::::::::: v2.0.4 ::

"""


def main_menu() -> None:
    """
    Отображает главное меню для управления репозиторием и запуска утилит.

    Функционал:
      - Выполнение git push/pull.
      - Запуск Renamer для переименования изображений.
      - Работа как в корне проекта, так и в режиме сабмодуля.

    Определяет корень репозитория и путь к директории `cuberbug_walls`
    (если доступен), затем запускает интерактивное меню действий.
    """
    console.print(title_text)

    submodule_mode = is_submodule()
    repo_root_path = get_root_path(submodule_mode)
    cuberbug_walls_path: Path | None = None

    if submodule_mode:
        cuberbug_walls_path = get_cuberbug_walls_path()

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
            git_push(repo_root_path)
        elif choice == "Обновить (git pull)":
            git_pull(repo_root_path)
        elif choice == "Renamer (переименование изображений)":
            renamer_menu(cuberbug_walls_path)
        elif choice == "Выход" or choice is None:
            console.print("\n[bold yellow]Выход из программы...[/bold yellow]")
            break


def renamer_menu(cuberbug_walls_path: Path | None) -> None:
    """
    Отображает подменю для запуска утилиты Renamer.

    Позволяет:
      - Запустить переименование изображений в стандартной директории
        `cuberbug_walls/`.
      - Выполнить «сухой запуск» (без изменений).
      - Указать произвольный путь для переименования.
      - Вернуться в главное меню.

    Args:
        cuberbug_walls_path (Path | None): Путь к директории с изображениями
            (если обнаружена автоматически).
    """
    console.print("\n[bold cyan]Renamer — Подменю[/bold cyan]\n")

    choices = []
    if cuberbug_walls_path:
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
            rename_files(cuberbug_walls_path, dry_run=dry_run)
        elif "Указать свой путь" in choice:
            path = questionary.path("Укажите путь к директории:").ask()
            if not path:
                console.print("[red]Отменено[/red]")
                continue
            dry_run = questionary.confirm(
                "Выполнить сухой запуск (без переименования)?"
            ).ask()
            rename_files(path, dry_run=dry_run)
