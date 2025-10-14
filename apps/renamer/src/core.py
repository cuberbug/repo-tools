import os
import shutil
from time import sleep

from rich.console import Console
from rich.progress import Progress
from rich.table import Table

from apps.renamer.src.utils import (
    generate_new_filename,
    is_already_renamed,
    is_image,
)

SLEEP_TIME: int | float = 0.01  # Задержка на 10 мс
console = Console()


def rename_files(directory: str, dry_run: bool = False) -> None:
    """
    Переименовывает файлы в указанной директории по времени их модификации.

    Args:
        directory: Путь к директории для обработки.
        dry_run: Если True, то выполняется только симуляция переименования.
    """
    if not os.path.isdir(directory):
        console.print(
            f"[red]Ошибка: директория '{directory}' не существует.[/red]"
        )
        return

    renamed_count: int = 0
    skipped_count: int = 0
    errors: int = 0

    console.print(
        f"[bold cyan]Сканирование директории:[/bold cyan] {directory}"
    )
    if dry_run:
        console.print("[yellow]Включен режим 'сухого запуска'.[/yellow]")

    # Собираем список файлов заранее, чтобы отображать прогресс
    all_files: list(tuple(str, str)) = []
    for root, _, files in os.walk(directory):
        for filename in files:
            full_path = os.path.join(root, filename)
            if is_image(full_path):
                all_files.append((root, filename))

    if not all_files:
        console.print("[yellow]Нет файлов для обработки.[/yellow]")
        return

    progress = Progress()

    with progress:
        for root, filename in progress.track(
            all_files,
            description="Обработка файлов...",
        ):
            full_path = os.path.join(root, filename)

            try:
                if is_already_renamed(filename):
                    skipped_count += 1
                    continue

                timestamp = int(os.path.getmtime(full_path))
                new_filename = generate_new_filename(filename, timestamp)
                new_full_path = os.path.join(root, new_filename)

                # Разрешаем коллизии временных меток
                while os.path.exists(new_full_path):
                    timestamp += 1
                    new_filename = generate_new_filename(filename, timestamp)
                    new_full_path = os.path.join(root, new_filename)

                progress.console.print(
                    f"[cyan]{filename}[/cyan] → [green]{new_filename}[/green]"
                )

                if not dry_run:
                    shutil.move(full_path, new_full_path)
                    renamed_count += 1
            except Exception as e:
                errors += 1
                console.print(
                    f"[red]Ошибка при обработке {full_path}: {e}[/red]"
                )

            sleep(SLEEP_TIME)

    # Выводим сводку
    table = Table(title="Результаты переименования", show_lines=True)
    table.add_column("Показатель", style="bold cyan")
    table.add_column("Значение", style="bold white")

    table.add_row("Переименовано файлов", str(renamed_count))
    table.add_row("Пропущено (уже переименованы)", str(skipped_count))
    table.add_row("Ошибок", str(errors))
    console.print()
    console.print(table)
