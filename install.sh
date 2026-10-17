#!/bin/bash

# Выход при любой ошибке
set -e

# Цвета для вывода в консоль
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "BLUE=== Запуск универсального инсталлятора LinuxLog ==={NC}"

# Проверка на запуск без root-прав (sudo запросится внутри)
if [ "\$EUID" -eq 0 ]; then
    echo -e "REDОшибка: Не запускайте скрипт через sudo ./install.sh.{NC}"
    echo "Запустите как обычный пользователь: ./install.sh"
    exit 1
fi

# 1. Определение дистрибутива через /etc/os-release
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=\$ID
    # Поддержка производных (например, Linux Mint базируется на ubuntu/debian)
    ID_LIKE_LIST=\$ID_LIKE
else
    echo -e "REDОшибка: Не удалось определить операционную систему.{NC}"
    exit 1
fi

# Пути установки
USER_HOME=\$HOME
INSTALL_DIR="\$USER_HOME/.local/share/linuxlog"
DESKTOP_ENTRY_DIR="\$USER_HOME/.local/share/applications"

# Переменные для пакетов
PM=""
PKGS=""
ARCH_SETUP_DB=false

echo -e "Обнаружена система: \${GREEN}NAME{NC}"

# 2. Настройка под конкретный менеджер пакетов
case "\$DISTRO" in
    fedora)
        PM="dnf"
        PKGS="mariadb mariadb-server python3 python3-devel python3-virtualenv qt6-qtbase-devel mesa-libGL rsync"
        ;;
    ubuntu|debian|mint)
        PM="apt"
        PKGS="mariadb-server mariadb-client python3 python3-dev python3-venv qt6-base-dev libgl1-mesa-glx rsync"
        ;;
    arch)
        PM="pacman"
        PKGS="mariadb python python-virtualenv qt6-base mesa rsync"
        ARCH_SETUP_DB=true
        ;;
    *)
        # Проверка по вторичным признакам (ID_LIKE), если дистрибутив редкий
        if [[ "\(ID_LIKE_LIST" =~ "ubuntu" \vert{}\vert{} "\)ID_LIKE_LIST" =~ "debian" ]]; then
            PM="apt"
            PKGS="mariadb-server mariadb-client python3 python3-dev python3-venv qt6-base-dev libgl1-mesa-glx rsync"
        elif [[ "\$ID_LIKE_LIST" =~ "arch" ]]; then
            PM="pacman"
            PKGS="mariadb python python-virtualenv qt6-base mesa rsync"
            ARCH_SETUP_DB=true
        else
            echo -e "\${RED}Извините, ваш дистрибутив (DISTRO) пока не поддерживается автоматически.{NC}"
            exit 1
        fi
        ;;
esac

# 3. Установка системных зависимостей
echo -e "\${BLUE}[1/6] Установка MariaDB и системных библиотек через PM...{NC}"
if [ "\$PM" == "apt" ]; then
    sudo apt update -y
    sudo apt install -y \$PKGS
elif [ "\$PM" == "dnf" ]; then
    sudo dnf install -y \$PKGS
elif [ "\$PM" == "pacman" ]; then
    sudo pacman -Syu --needed --noconfirm \$PKGS
fi

# 4. Инициализация базы данных (специфика Arch Linux)
if [ "\$ARCH_SETUP_DB" = true ]; then
    # На Arch нужно создать системные таблицы перед запуском
    if [ ! -d "/var/lib/mysql/mysql" ]; then
        echo -e "BLUEИнициализация системных таблиц MariaDB (Специфика Arch)...{NC}"
        sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
    fi
fi

echo -e "\({BLUE}[2/6] Активация и запуск службы MariaDB...\){NC}"
sudo systemctl enable --now mariadb

# Создание базы и пользователя
DB_NAME="linuxlog_db"
DB_USER="log_user"
DB_PASS="LogPass123!"

echo -e "BLUEНастройка базы данных проекта в MariaDB...{NC}"
# UNIX сокет позволяет root-пользователю выполнять команды без пароля внутри sudo
sudo mariadb -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`${DB_NAME}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS '\({DB_USER}'@'localhost' IDENTIFIED BY '\){DB_PASS}';
GRANT ALL PRIVILEGES ON \`${DB_NAME}\`.* TO '\${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

# 5. Копирование файлов лога
echo -e "\({BLUE}[3/6] Развертывание файлов логгера...\){NC}"
mkdir -p "\$INSTALL_DIR"
rsync -av --exclude='__pycache__' --exclude='.git' --exclude='.idea' ./ "\$INSTALL_DIR/"

# 6. Создание изолированного виртуального окружения Python
echo -e "\({BLUE}[4/6] Настройка виртуального окружения (venv)...\){NC}"
cd "\$INSTALL_DIR"
python3 -m venv .venv || python -m venv .venv
source .venv/bin/activate

# Обновляем менеджеры пакетов внутри venv
pip install --upgrade pip setuptools wheel

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Запасной вариант установки, если файла зависимостей нет
    pip install PyQt6 pyserial requests
fi
deactivate

# 7. Создание стартового скрипта с фиксацией путей
echo -e "\({BLUE}[5/6] Создание исполняемого скрипта-стартера...\){NC}"
cat <<EOF > "\$INSTALL_DIR/linuxlog-run.sh"
#!/bin/bash
cd "\$INSTALL_DIR"
source .venv/bin/activate
python3 main.py "\$@"
deactivate
EOF
chmod +x "\$INSTALL_DIR/linuxlog-run.sh"

# 8. Создание ярлыка в меню приложений системы
echo -e "\({BLUE}[6/6] Создание ярлыка в меню приложений...\){NC}"
mkdir -p "\$DESKTOP_ENTRY_DIR"

ICON_PATH="\$INSTALL_DIR/logo.png"
if [ ! -f "\(ICON_PATH" ] && [ -f "\)INSTALL_DIR/icon.svg" ]; then
    ICON_PATH="\$INSTALL_DIR/icon.svg"
fi

cat <<EOF > "\$DESKTOP_ENTRY_DIR/linuxlog.desktop"
[Desktop Entry]
Version=1.0
Type=Application
Name=LinuxLog Ham Radio
Comment=Логгер для радиолюбителей (CAT, TCI, eQSL)
Exec=\$INSTALL_DIR/linuxlog-run.sh
Icon=\$ICON_PATH
Terminal=false
Categories=Utility;Development;HamRadio;
StartupNotify=true
Path=\$INSTALL_DIR
EOF

# Обновление системного меню (для немедленного отображения ярлыка)
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database "\$DESKTOP_ENTRY_DIR"
fi

echo -e "\${GREEN}=== Установка успешно завершена на системе NAME! ==={NC}"
echo -e "Данные для подключения вашего Python-кода к MariaDB:"
echo -e "База: \${BLUE}\(DB_NAME\){NC} | Пользователь: BLUEDB_USERNC | Пароль: {BLUE}\(DB_PASS\){NC}"
