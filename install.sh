#!/bin/bash

set -e

SERVICE_NAME=battery-logger
SCRIPT_NAME=battery_logger.py
INSTALL_PATH=/usr/local/bin/$SCRIPT_NAME
SERVICE_PATH=/etc/systemd/system/$SERVICE_NAME.service

echo "🔍 Перевіряємо наявність psutil..."
if ! python3 -c "import psutil" 2>/dev/null; then
    echo "📦 Встановлюємо psutil..."
    if command -v apt >/dev/null; then
        sudo apt update
        sudo apt install -y python3-psutil
    else
        sudo pip3 install psutil
    fi
else
    echo "✅ psutil вже встановлений."
fi

echo "📄 Копіюємо скрипт у $INSTALL_PATH"
sudo cp $SCRIPT_NAME $INSTALL_PATH
sudo chmod +x $INSTALL_PATH

echo "⚙️ Створюємо systemd службу..."

sudo tee $SERVICE_PATH > /dev/null <<EOF
[Unit]
Description=Battery logging service
After=network.target

[Service]
ExecStart=/usr/bin/python3 $INSTALL_PATH
Restart=always
RestartSec=10
StandardOutput=append:/var/log/battery-logger.log
StandardError=append:/var/log/battery-logger.err
User=$(whoami)

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Перезапускаємо systemd daemon..."
sudo systemctl daemon-reexec
sudo systemctl daemon-reload

echo "🔓 Дозволяємо запуск служби..."
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

echo "✅ Встановлення завершено. Статус служби:"
systemctl status $SERVICE_NAME --no-pager
