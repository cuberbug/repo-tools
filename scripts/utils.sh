#!/usr/bin/env bash
# ==============================================================================
# Вспомогательные утилиты для настройки и запуска Python-проектов.
# ------------------------------------------------------------------------------
# Содержит:
#   - Проверку системных зависимостей
#   - Универсальную функцию подтверждения действий
#   - Выбор интерпретатора Python
#   - Настройку виртуального окружения
# ==============================================================================


# ------------------------------------------------------------------------------
# Имя функции: check_dependencies
#
# Назначение:
#   Проверяет наличие системных зависимостей (Git и Python).
#
# Возвращаемые значения:
#   0 — если все зависимости найдены
#   1 — если отсутствует хотя бы одна зависимость
# ------------------------------------------------------------------------------
check_dependencies() {
  echo -e "${DECOR_BLUE}Проверка системных зависимостей...${RESET}"
  if ! command -v git &>/dev/null; then
    echo -e "${TITLE_ERROR}Git не найден. Пожалуйста, установите Git."
    return 1
  fi
  if ! command -v python3 &>/dev/null && ! command -v python &>/dev/null; then
    echo -e "${TITLE_ERROR}Python не найден. Пожалуйста, установите Python."
    return 1
  fi
  echo -e "${DECOR_GREEN}Все системные зависимости найдены.${RESET}"
  return 0
}


# ------------------------------------------------------------------------------
# Имя функции: confirm
#
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
# ------------------------------------------------------------------------------
confirm() {
  local message=$1
  local default_choice=${2:-yes}
  local prompt_suffix

  if [[ "$default_choice" == "-n" ]]; then
    prompt_suffix="[y/N]"
  else
    prompt_suffix="[Y/n]"
  fi

  while true; do
    echo -ne "\n${DECOR_BLUE_FG}${message}?${RESET} ${prompt_suffix}: "
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
        echo -e "${DECOR_YELLOW_FG}Неверный ввод, попробуйте снова.${RESET}"
        ;;
    esac
  done
}


# ------------------------------------------------------------------------------
# Имя функции: choose_python
#
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
# ------------------------------------------------------------------------------
choose_python() {
  local python_cmd=$1
  local found_python=""

  if [[ -n "$python_candidate" && -x "$python_candidate" ]]; then
    found_python="$python_candidate"
  fi

  if [[ -z "$found_python" ]]; then
    if command -v python3 &>/dev/null; then
      found_python=$(command -v python3)
    elif command -v python &>/dev/null; then
      found_python=$(command -v python)
    fi
  fi

  if [[ -n "$found_python" ]]; then
    echo "$found_python"
    return 0 # Найдено
  else
    return 1 # Не найдено
  fi
}


# ------------------------------------------------------------------------------
# Имя функции: install_requirements
#
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
# ------------------------------------------------------------------------------
install_requirements() {
  local python_bin="" pip_bin="" requirements=""

  while [[ $# -gt 0 ]]; do
    case $1 in
      --python)       python_bin=$2; shift 2 ;;
      --pip)          pip_bin=$2; shift 2 ;;
      --requirements) requirements=$2; shift 2 ;;
      *) echo "Неизвестный аргумент: $1" >&2; return 1 ;;
    esac
  done

  if [[ -z "$python_bin" || -z "$pip_bin" || -z "$requirements" ]]; then
    echo -e "${TITLE_ERROR}Отсутствуют обязательные аргументы для install_requirements.${RESET}"
    return 1
  fi

  if [[ ! -x "$python_bin" || ! -x "$pip_bin" ]]; then
    echo -e "${TITLE_ERROR}Указанные файлы python/pip недоступны или не исполняемы.${RESET}"
    return 1
  fi

  if [[ ! -f "$requirements" || ! -s "$requirements" ]]; then
    echo -e "${DECOR_GREEN}Установка зависимостей не требуется (requirements.txt отсутствует или пуст).${RESET}"
    return 0
  fi

  echo -e "${DECOR_BLUE}Обновление pip и установка зависимостей из ${requirements}...${RESET}"

  "$python_bin" -m pip install --upgrade pip || {
    echo -e "${TITLE_ERROR}Не удалось обновить pip.${RESET}"
    return 1
  }

  "$pip_bin" install -r "$requirements" || {
    echo -e "${TITLE_ERROR}Ошибка при установке зависимостей.${RESET}"
    return 1
  }

  echo -e "${DECOR_GREEN_FG}Зависимости успешно установлены.${RESET}"
  return 0
}


# ------------------------------------------------------------------------------
# Имя функции: setup_venv
#
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
# ------------------------------------------------------------------------------
setup_venv() {
  local venv_dir="" python_bin="" pip_bin="" requirements=""
  local venv_created=false

  while [[ $# -gt 0 ]]; do
    case $1 in
      --venv-dir)     venv_dir=$2; shift 2 ;;
      --python)       python_bin=$2; shift 2 ;;
      --pip)          pip_bin=$2; shift 2 ;;
      --requirements) requirements=$2; shift 2 ;;
      *) echo "Неизвестный аргумент: $1"; return 1 ;;
    esac
  done

  if [[ -z "$venv_dir" || -z "$python_bin" || -z "$pip_bin" || -z "$requirements" ]]; then
    echo -e "${TITLE_ERROR}Отсутствуют обязательные аргументы для setup_venv.${RESET}"
    return 1
  fi

  if [[ -d "$venv_dir" ]]; then
    echo -e "${DECOR_GREEN}Найдено установленное виртуальное окружение Python."
  else
    echo -e "${DECOR_YELLOW_FG}Виртуальное окружение Python не установлено.${RESET}"
    echo -e "Можно установить его автоматически в директорию: ${BOLD}${venv_dir}${RESET}"

    if confirm "Создать новое виртуальное окружение"; then
      echo "Создание виртуального окружения..."
      local python_cmd
      python_cmd="$(choose_python "$python_bin")" || return 1

      if ! "$python_cmd" -m venv "$venv_dir"; then
        echo -e "${TITLE_ERROR}Не удалось создать виртуальное окружение."
        return 1
      fi
      venv_created=true
    else
      echo -e "${DECOR_YELLOW_FG}Создание окружения отменено.${RESET}"
      echo -e "${FG_YELLOW}Продолжение работы небезопасно: будет использоваться системный Python.${RESET}"
      return 1
    fi
  fi

  if [[ "$venv_created" != true ]]; then
    if ! confirm "Проверить зависимости и обновить окружение"; then
      echo -e "${DECOR_YELLOW_FG}Проверка зависимостей отменена.${RESET}"
      return 1
    fi
  fi

  install_requirements \
    --python "$python_bin" \
    --pip "$pip_bin" \
    --requirements "$requirements" \
    || return 1

  echo -e "${DECOR_GREEN_FG}Виртуальное окружение полностью готово к использованию.${RESET}"
  return 0
}
