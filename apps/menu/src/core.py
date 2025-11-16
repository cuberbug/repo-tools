from pathlib import Path

import questionary
import yaml
from rich.console import Console

from apps.menu.src.utils import (
    is_submodule,
    get_cuberbug_walls_path,
    get_root_path
)
from apps.gitops.src.core import git_pull, git_push
from apps.renamer.src.core import rename_files

console = Console()


class Menu:
    """Управляет меню."""
    CONFIG_NAME: str = "config.yml"

    def __init__(self, config_path: Path):
        """Загружает конфиг и инициализирует основные параметры."""
        self.config = self._load_config(config_path)

        self.version = self.config["version"]
        self.title_menu = (
            self.config["repo_tools_title"].format(version=self.version)
        )
        self.questionary_title = self.config.get("questionary_title", "")
        self.menu = self.config["menu"]
        self.renamer = self.config["renamer"]

    def _load_config(self, config_path: Path) -> dict:
        """Загружает YAML-конфигурацию."""
        try:
            with open(config_path, "r", encoding="utf-8") as file:
                return yaml.safe_load(file)
        except yaml.YAMLError as e:
            console.print(
                f"[red]Ошибка в YAML файле '{config_path}':[/red] {e}"
            )
            raise

    def _ask_choice(self, message: str, choices: list[str]) -> str | None:
        """Единая обёртка для вопроса выбора."""
        return questionary.select(message, choices=choices).ask()

    def main_menu(self) -> None:
        """Отображает главное меню Repo-Tools."""
        console.print(self.title_menu)

        submodule_mode = is_submodule()
        repo_root_path = get_root_path(submodule_mode)
        cuberbug_walls_path = (
            get_cuberbug_walls_path() if submodule_mode else None
        )

        base_actions = [
            self.menu["git_push"]["title"],
            self.menu["git_pull"]["title"],
            self.menu["renamer_menu"]["title"],
            self.menu["exit"]["title"]
        ]

        while True:
            choice = self._ask_choice(self.questionary_title, base_actions)

            if choice in (None, self.menu["exit"]["title"]):
                console.print("\nВыход из программы...", style="bold yellow")
                break

            if choice == self.menu["git_push"]["title"]:
                git_push(repo_root_path)

            elif choice == self.menu["git_pull"]["title"]:
                git_pull(repo_root_path)

            elif choice == self.menu["renamer_menu"]["title"]:
                self.renamer_menu(cuberbug_walls_path)

    def renamer_menu(self, cuberbug_walls_path: Path | None) -> None:
        """Подменю для запуска Renamer."""
        console.print(self.renamer["title"], style="bold cyan")

        choices = []

        # Добавляем автоматические действия, если путь найден
        if cuberbug_walls_path:
            choices.extend([
                self.renamer["dry_run_cuberbug_walls"]["title"],
                self.renamer["full_cuberbug_walls"]["title"]
            ])

        choices.extend([
            self.renamer["custom_path"]["title"],
            self.renamer["back"]["title"]
        ])

        while True:
            choice = self._ask_choice(self.questionary_title, choices)

            if choice in (None, self.renamer["back"]["title"]):
                break

            # Варианты для cuberbug_walls
            if cuberbug_walls_path and choice in (
                self.renamer["dry_run_cuberbug_walls"]["title"],
                self.renamer["full_cuberbug_walls"]["title"]
            ):
                if choice == self.renamer["dry_run_cuberbug_walls"]["title"]:
                    dry_run = self.renamer["dry_run_cuberbug_walls"]["dry_run"]

                rename_files(cuberbug_walls_path, dry_run=dry_run)
                continue

            # Пользовательский путь
            if choice == self.renamer["custom_path"]["title"]:
                path_str = questionary.path(
                    self.renamer["question_path"]["title"]
                ).ask()

                if not path_str:
                    console.print("Отменено", style="red")
                    continue

                path = Path(path_str)

                if not path.exists():
                    console.print("Ошибка: путь не существует!", style="red")
                    continue

                dry_run = questionary.confirm(
                    self.renamer["question_dry_run"]["title"]
                ).ask()

                rename_files(path, dry_run=dry_run)


def main() -> None:
    """Точка входа: загружает конфиг и запускает меню."""
    file_dir = Path(__file__).resolve().parent
    config_path = file_dir.parent.parent / Menu.CONFIG_NAME

    try:
        menu = Menu(config_path)
        menu.main_menu()
    except FileNotFoundError:
        console.print(
            f"Ошибка: Файл конфигурации '{config_path}' не найден.",
            style="red"
        )
    except KeyError as e:
        console.print(
            "Ошибка: отсутствует обязательный ключ в",
            f"'{Menu.CONFIG_NAME}': {e}",
            style="red"
        )
    except Exception as e:
        console.print(f"[red]Произошла непредвиденная ошибка:[/red] {e}")
