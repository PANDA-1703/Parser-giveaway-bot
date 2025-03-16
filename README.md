# Телеграмм-бот для розыгрышей.

Данный бот запоминает и напоминает о предстоящих подведениях итогов розыгрышей тг.

Пересылаем в бот розыгрыш тг, чтобы в БД записались дата и время подведения итогов. Затем в это время придёт 
напоминалка. 

[Пример](resources/photo/example.jpg)

## Установка и запуск
```shell
git clone https://github.com/PANDA-1703/Parser-giveaway-bot.git
cd Parser-giveaway-bot
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

В файле `app/config.py` ввести свои токен и id.

Запуск:
```shell
python app/bot.py
```

## Установка сервиса
```shell
sudo nano /etc/systemd/system/bot-parser-giveaway.service
```

```shell
[Unit]
Description=Telegram Bot Parser giveaway Service
After=network.target

[Service]
ExecStart=/home/your-path/Parser-giveaway-bot/.venv/bin/python /home/your-path/Parser-giveaway-bot/app/bot.py
WorkingDirectory=/home/your-path/Parser-giveaway-bot
User=your-user
Group=your-user
Environment="PATH=/home/your-path/Parser-giveaway-bot/.venv/bin:$PATH"
Restart=always

[Install]
WantedBy=multi-user.target
```

```shell
sudo systemctl daemon-reload
sudo systemctl start bot-parser-giveaway.service
sudo systemctl status bot-parser-giveaway.service
sudo systemctl enable bot-parser-giveaway.service
```