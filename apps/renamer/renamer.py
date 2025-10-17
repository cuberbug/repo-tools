"""
Renamer — инструмент для переименования изображений
по Unix-времени их модификации.
"""
import argparse
import os
import sys

from rich.console import Console

from .src.core import rename_files

console = Console()


def main():
    """
    Точка входа CLI-приложения.

    Обрабатывает аргументы командной строки и запускает процесс переименования:
      - Проверяет существование указанной директории.
      - Выполняет переименование с учётом флага `--dry-run`.

    Пример использования:
        python -m apps.renamer.renamer ./images --dry-run

    Аргументы CLI:
        DIRECTORY — путь к директории с изображениями.
        --dry-run — симуляция без переименования.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Переименовывает изображения, используя время модификации файла."
        )
    )
    parser.add_argument(
        "directory",
        metavar="DIRECTORY",
        type=str,
        help="Путь к директории, которую нужно обработать."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Показывает, что будет сделано, без фактического переименования."
    )
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        console.print(
            "[bold red]Ошибка:[/bold red]",
            f"Директория '{args.directory}' не найдена."
        )
        sys.exit(1)

    rename_files(args.directory, args.dry_run)


if __name__ == "__main__":
    main()
