#!/usr/bin/env bash

# Подключает общую логику, переменные и проверки
source "$(dirname "${BASH_SOURCE[0]}")/../shared/common.sh" || exit 1
cd "$REPO_ROOT" || exit 1


# --- Git ---

git fetch --quiet

if [[ -z "$UPDATES" ]]; then
    echo -e "${DECOR_YELLOW}Предупреждение: Upstream для текущей ветки не задан.${RESET}"
    echo -e "${FG_YELLOW}Невозможно проверить актуальность.${RESET}"
    exit 1
fi

if (( UPDATES == 0 )); then
    echo -e "${DECOR_GREEN}Репозиторий уже находится в актуальном состоянии.${RESET}"
    exit 0
else
    echo -e "${DECOR_BLUE}Репозиторий отстаёт от удалённой ветки на $UPDATES коммитов.${RESET}"
fi

git status

if confirm "Обновить локальный репозиторий"; then
  echo -e "${DECOR_BLUE}Загрузка актуального состояния репозитория..."
  if ! git pull "$@"; then
    echo -e "${TITLE_ERROR}Не удалось выполнить pull"
    exit 1
  fi
  echo -e "${DECOR_BLUE}${FG_GREEN}Локальный репозиторий обновлён${RESET}"
else
  echo -e "${DECOR_YELLOW_FG}Отмена${RESET}"
fi
