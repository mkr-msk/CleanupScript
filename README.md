# CleanupScript

Скрипт для автоматической очистки мусора на Windows с уведомлениями в Telegram.

## Функции
- Очистка кэша Яндекс.Браузера (с сохранением кук).
- Очистка системных папок: `%TEMP%`, `C:\Windows\Temp`, `C:\Windows\SoftwareDistribution\Download`.
- Удаление логов старше 7 дней из `C:\Windows\Logs`.
- Очистка корзины.
- Уведомления в Telegram.

## Установка
1. Клонируй репозиторий:
2. git clone https://github.com/твой_логин/CleanupScript.git cd CleanupScript
3. Установите зависимости: pip install -r requirements.txt
4. Создай `.env` на основе `.env.example`:
TELEGRAM_BOT_TOKEN=your_bot_token 
TELEGRAM_CHAT_ID=your_chat_id

## Использование
- Тестовый режим:
python cleanup.py --dry-run
- Реальная очистка:
python cleanup.py
- Автоматизация: 
Используй `run_cleanup.bat` в Планировщике задач.

## Тесты
python tests.py