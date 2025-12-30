#!/bin/sh
# entrypoint.sh — keep alive для polling бота
python bot.py
# Якщо бот впаде — перезапустимо (Fly не вважатиме crashing)
while true; do
    echo "Бот зупинився — перезапуск..."
    python bot.py
done