#!/usr/bin/env bash
# ==============================================================================
# Вспомогательные утилиты для настройки и запуска Python-проектов.
# ------------------------------------------------------------------------------
# Содержит:
#   - Универсальную функцию подтверждения действий
#   - Выбор интерпретатора Python
#   - Настройку виртуального окружения
# ==============================================================================


set -o errexit
set -o nounset
set -o pipefail


# ==============================================================================
# Имя функции: confirm
# ------------------------------------------------------------------------------
# Назначение:
#   Запрашивает у пользователя подтверждение действия (да/нет).
#
# Аргументы:
#   $1 — текст сообщения (обязательно)
#   $2 — поведение по умолчанию (необязательно):
#         - "-n" → по умолчанию "нет"
#         - любое другое значение → по умолчанию "да"
#
# Возвращаемые значения:
#   0 — если пользователь подтвердил
#   1 — если отклонил
# ==============================================================================
confirm() {
  local message=$1
  local default_choice=${2:-yes}
  local prompt_suffix

  if [[ "$default_choice" == "-n" ]]; then
    prompt_suffix=$(f_bold "N")
    prompt_suffix=$(f_red "$prompt_suffix")
    prompt_suffix="[y/${prompt_suffix}]"
  else
    prompt_suffix=$(f_bold "Y")
    prompt_suffix=$(f_green "$prompt_suffix")
    prompt_suffix="[${prompt_suffix}/n]"
  fi

  while true; do
    local format_message

    format_message="$(f_bold "${message}?")"
    format_message="$(f_blue "${format_message}")"
    printf "%s %s " "${format_message}" "${prompt_suffix}:"
    read -r response
    response=${response,,}

    case $response in
      y|yes) return 0 ;;
      n|no)  return 1 ;;
      "")
        if [[ $default_choice == "-n" ]]; then
          return 1
        else
          return 0
        fi
        ;;
      *)
        e_stop "$(f_yellow "Неверный ввод, попробуйте снова.")"
        ;;
    esac
  done
}


# ==============================================================================
# Имя функции: choose_python
# ------------------------------------------------------------------------------
# Назначение:
#   Определяет, какой Python-интерпретатор использовать.
#   Если переданный путь существует и исполняемый — возвращает его.
#   Иначе возвращает системный python3 или python.
#
# Аргументы:
#   $1 — путь до интерпретатора (необязательно)
#
# Возвращаемое значение:
#   Строка — путь к подходящему интерпретатору Python
#
# Код возврата:
#   0 — интерпретатор найден.
#   1 — не удалось найти интерпретатор.
# ==============================================================================
choose_python() {
  local python_candidate=${1:-}
  local found_python=""

  if [[ -n "$python_candidate" && -x "$python_candidate" ]]; then
    echo "$python_candidate"
    return 0
  fi

  # Поиск системного Python
  if found_python=$(command -v python3); then
    echo "$found_python"
    return 0
  elif found_python=$(command -v python); then
    echo "$found_python"
    return 0
  fi

  return 1
}


# ==============================================================================
# Имя функции: setup_venv
# ------------------------------------------------------------------------------
# Назначение:
#   Создаёт и настраивает виртуальное окружение Python.
#   При необходимости обновляет зависимости из requirements.txt.
#
# Аргументы (все обязательны):
#   --venv-dir <path>        — путь до директории виртуального окружения
#   --python <path>          — путь до бинарного файла python в окружении
#   --pip <path>             — путь до бинарного файла pip в окружении
#   --requirements <path>    — путь до файла зависимостей
#
# Возвращаемые значения:
#   0 — если окружение настроено успешно
#   1 — при ошибке создания или установки зависимостей
#
# Пример:
#   setup_venv \
#     --venv-dir "./.venv" \
#     --python "./.venv/bin/python" \
#     --pip "./.venv/bin/pip" \
#     --requirements "./requirements.txt"
# ==============================================================================
setup_venv() {
  local venv_created=false
  local venv_dir python_bin pip_bin requirements

  if [[ $# -ne 8 ]]; then
    e_error "$(f_bold "setup_venv") требует 4 пары аргументов в формате ключ-значение."
    return 1
  fi

  while [[ $# -gt 0 ]]; do
    case $1 in
      --venv-dir)     venv_dir=$2;     shift 2 ;;
      --python)       python_bin=$2;   shift 2 ;;
      --pip)          pip_bin=$2;      shift 2 ;;
      --requirements) requirements=$2; shift 2 ;;
      *) e_error "Неизвестный аргумент: $1"; return 1 ;;
    esac
  done

  if [[ -z "$venv_dir" || -z "$python_bin" || -z "$pip_bin" || -z "$requirements" ]]; then
    e_error "Отсутствуют обязательные аргументы для setup_venv."
    return 1
  fi

  if [[ -d "$venv_dir" ]]; then
    e_done "Найдено установленное виртуальное окружение Python."
  else
    e_info "$(f_yellow "Виртуальное окружение Python не установлено.")"
    e_info "Можно установить его автоматически в директорию: $(f_bold "${venv_dir}")"

    if confirm "Создать новое виртуальное окружение"; then
      e_info "Создание виртуального окружения..."

      # Для создания используем системный Python
      local system_python
      system_python="$(choose_python)" || {
         e_error "Не найден системный Python для создания окружения."
         return 1
      }

      if ! "$system_python" -m venv "$venv_dir"; then
        e_error "Не удалось создать виртуальное окружение."
        return 1
      fi
      e_done "$(f_green "Новое виртуальное окружение создано.")"
      venv_created=true
    else
      e_stop "$(f_yellow "Создание окружения отменено.")"
      return 1
    fi
  fi

  # Логика обновления зависимостей
  local should_install=false

  if [[ "$venv_created" == true ]]; then
    should_install=true
  else
    # Предлагаем "No" по умолчанию
    if confirm "Проверить зависимости и обновить окружение" -n; then
       should_install=true
    else
       e_stop "Проверка зависимостей пропущена пользователем."
       return 0 
    fi
  fi

  if [[ "$should_install" == true ]]; then
    install_requirements \
      --python "$python_bin" \
      --pip "$pip_bin" \
      --requirements "$requirements" \
      || return 1
  fi
}


# ==============================================================================
# Имя функции: install_requirements
# ------------------------------------------------------------------------------
# Назначение:
#   Устанавливает Python-зависимости из указанного файла requirements.txt.
#   Перед установкой обновляет pip до последней версии.
#
# Аргументы (все обязательны):
#   --python <path>       — путь до бинарного файла python в окружении
#   --pip <path>          — путь до бинарного файла pip в окружении
#   --requirements <path> — путь до файла зависимостей
#
# Возвращаемые значения:
#   0 — зависимости успешно установлены
#   1 — при ошибке установки или некорректных аргументах
#
# Пример:
#   install_requirements \
#     --python "./.venv/bin/python" \
#     --pip "./.venv/bin/pip" \
#     --requirements "./requirements.txt"
# ==============================================================================
install_requirements() {
  local python_bin pip_bin requirements

  if [[ $# -ne 6 ]]; then
    e_error "$(f_bold "install_requirements") требует 3 пары аргументов в формате ключ-значение."
    return 1
  fi

  while [[ $# -gt 0 ]]; do
    case $1 in
      --python)       python_bin=$2;   shift 2 ;;
      --pip)          pip_bin=$2;      shift 2 ;;
      --requirements) requirements=$2; shift 2 ;;
      *) e_error "Неизвестный аргумент: $1"; return 1 ;;
    esac
  done

  if [[ -z "$python_bin" || -z "$pip_bin" || -z "$requirements" ]]; then
    e_error "Отсутствуют обязательные аргументы для install_requirements."
    return 1
  fi

  if [[ ! -x "$python_bin" || ! -x "$pip_bin" ]]; then
    e_error "Указанные файлы python/pip недоступны или не исполняемы."
    return 1
  fi

  if [[ ! -f "$requirements" || ! -s "$requirements" ]]; then
    e_done "$(f_green "Установка зависимостей не требуется") (requirements.txt отсутствует или пуст)."
    return 0
  fi

  e_info "Обновление $(f_bold "pip") и установка зависимостей из $(f_bold "${requirements}")..."

  "$python_bin" -m pip install --upgrade pip || {
    e_error "Не удалось обновить pip."
    return 1
  }

  "$pip_bin" install -r "$requirements" || {
    e_error "Ошибка при установке зависимостей."
    return 1
  }

  e_done "$(f_green "Зависимости успешно установлены.")"
  return 0
}
