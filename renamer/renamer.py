import argparse
import os
import sys

from src.core import rename_files


def main():
    """
    Основная функция-точка входа в программу.
    Обрабатывает аргументы командной строки и запускает логику переименования.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Переименовывает файлы-изображения в указанной директории, "
            "используя время их создания в качестве имени."
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
        help=(
            "Выводит список файлов, которые будут переименованы, но не "
            "выполняет переименование."
        )
    )

    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print(f"Ошибка: Директория '{args.directory}' не найдена.")
        sys.exit(1)

    rename_files(args.directory, args.dry_run)


if __name__ == "__main__":
    main()
