#!/usr/bin/env bash
# ==============================================================================
# Точка входа: start.sh
# ------------------------------------------------------------------------------
# Назначение:
#   Скрипт инициализирует рабочее окружение и запускает главное меню приложения.
#   Он проверяет наличие системных зависимостей, настраивает виртуальное
#   окружение Python и безопасно выполняет целевой скрипт `menu/menu.py`.
#
# Этапы выполнения:
#   1. Подключение вспомогательных библиотек (decor.sh, utils.sh)
#   2. Проверка системных зависимостей (Git, Python)
#   3. Настройка виртуального окружения:
#        - создание при отсутствии
#        - обновление зависимостей
#   4. Запуск основного меню
#
# Структура путей:
#   TOOLS_ROOT/                — корень инструментов
#   ├── scripts/decor.sh       — оформление вывода
#   ├── scripts/utils.sh       — логика и утилиты
#   ├── apps/requirements.txt  — список зависимостей
#   ├── apps/.venv/            — виртуальное окружение Python
#   └── apps/menu/menu.py      — главный модуль приложения
#
# Возвращаемые значения:
#   0 — успешная инициализация и/или корректное завершение работы
#   1 — при ошибках проверки зависимостей, создания окружения или запуске меню
#
# Пример запуска:
#   ./start.sh
#
# Примечания:
#   - Скрипт безопасен к запуску повторно: при наличии окружения
#     выполняется только проверка и обновление зависимостей.
#   - В режиме ошибок вывод остаётся на экране до нажатия Enter.
# ==============================================================================

set -o pipefail


# --- Определение путей и подключение библиотек ---

TOOLS_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$TOOLS_ROOT" || exit 1
# shellcheck disable=SC1091
source "${TOOLS_ROOT}/scripts/decor.sh" || { echo "Ошибка: не найден decor.sh" >&2; exit 1; }
# shellcheck disable=SC1091
source "${TOOLS_ROOT}/scripts/utils.sh" || { echo "Ошибка: не найден utils.sh" >&2; exit 1; }


# --- Настройка параментров виртуального окружения ---

APPS_DIR="${TOOLS_ROOT}/apps"

REQUIREMENTS_FILE="${APPS_DIR}/requirements.txt"
VENV_DIR="${APPS_DIR}/.venv"
VENV_PYTHON_FILE="${VENV_DIR}/bin/python"
VENV_PIP_FILE="${VENV_DIR}/bin/pip"

MENU_APP="apps.menu.menu"


# --- Основная логика ---

main() {
  set -o errexit

  check_dependencies
  setup_venv \
    --venv-dir "$VENV_DIR" \
    --python "$VENV_PYTHON_FILE" \
    --pip "$VENV_PIP_FILE" \
    --requirements "$REQUIREMENTS_FILE"

  local venv_python

  venv_python="$(choose_python "$VENV_PYTHON_FILE")"

  if confirm "Запустить главное меню"; then
    echo -e "${DECOR_BLUE}Запуск меню...${RESET}"
    cd "$TOOLS_ROOT"
    "$venv_python" -m "$MENU_APP"
  else
    echo -e "${DECOR_YELLOW_FG}Запуск меню отменён.${RESET}"
  fi
}


# --- Безопасный запуск ---

if main; then
  exit 0
else
  echo -e "\n${TITLE_ERROR}${BOLD}В процессе инициализации произошла ошибка.${RESET}"
  echo "Пожалуйста, просмотрите вывод выше, чтобы понять причину."
  echo "Окно не будет закрыто автоматически, чтобы вы могли изучить лог."
  read -r -p "Нажмите Enter для выхода..."
  exit 1
fi
