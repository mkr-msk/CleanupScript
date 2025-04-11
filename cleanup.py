import os
import shutil
import pathlib
import logging
import datetime
import telegram
import asyncio
import subprocess
from argparse import ArgumentParser
from dotenv import load_dotenv

# Загрузка переменных из .env
load_dotenv()

# Настройка логирования
logging.basicConfig(
    filename='logs/cleanup_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def send_telegram_message(token, chat_id, message):
    """Отправка уведомления в Telegram."""
    try:
        bot = telegram.Bot(token=token)
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info("Telegram-уведомление отправлено")
    except Exception as e:
        logger.error(f"Ошибка отправки Telegram-уведомления: {e}")

def get_folder_size(folder_path):
    """Подсчёт размера папки."""
    total_size = 0
    try:
        for dirpath, _, filenames in os.walk(folder_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                total_size += os.path.getsize(fp)
    except Exception:
        pass
    return total_size

def clean_yandex_browser_cache(dry_run=False, cache_path=None):
    """Очистка кэша Яндекс.Браузера."""
    if cache_path is None:
        cache_path = os.path.join(os.getenv("LOCALAPPDATA"), "Yandex", "YandexBrowser", "User Data", "Default")
    logger.info(f"Начало очистки кэша Яндекс.Браузера: {cache_path}")
    size_before = get_folder_size(cache_path)
    deleted_size = 0

    if not os.path.exists(cache_path):
        logger.warning(f"Папка не найдена: {cache_path}")
        return 0

    exclude = {"Cookies", "Cookies-journal"}
    for item in pathlib.Path(cache_path).glob("*"):
        if item.name in exclude:
            continue
        try:
            if dry_run:
                logger.info(f"[Dry Run] Будет удалено: {item}")
                continue
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_size += size
            elif item.is_dir() and item.name in {"Cache", "Cache2", "Code Cache"}:
                size = get_folder_size(item)
                shutil.rmtree(item, ignore_errors=True)
                deleted_size += size
            logger.info(f"Удалено: {item}")
        except Exception as e:
            logger.error(f"Ошибка при удалении {item}: {e}")

    size_after = get_folder_size(cache_path)
    logger.info(f"Очищено кэша Яндекс.Браузера: {(size_before - size_after) / 1024 / 1024:.2f} MB")
    return deleted_size

def clean_system_folder(folder_path, dry_run=False):
    """Очистка системной папки."""
    logger.info(f"Начало очистки папки: {folder_path}")
    size_before = get_folder_size(folder_path)
    deleted_size = 0

    if not os.path.exists(folder_path):
        logger.warning(f"Папка не найдена: {folder_path}")
        return 0

    for item in pathlib.Path(folder_path).glob("*"):
        try:
            if dry_run:
                logger.info(f"[Dry Run] Будет удалено: {item}")
                continue
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_size += size
            elif item.is_dir():
                size = get_folder_size(item)
                shutil.rmtree(item, ignore_errors=True)
                deleted_size += size
            logger.info(f"Удалено: {item}")
        except Exception as e:
            logger.error(f"Ошибка при удалении {item}: {e}")

    size_after = get_folder_size(folder_path)
    logger.info(f"Очищено в {folder_path}: {(size_before - size_after) / 1024 / 1024:.2f} MB")
    return deleted_size

def clean_old_logs(logs_path, days=7, dry_run=False):
    """Очистка логов старше указанного количества дней."""
    logger.info(f"Начало очистки логов: {logs_path}")
    size_before = get_folder_size(logs_path)
    deleted_size = 0

    if not os.path.exists(logs_path):
        logger.warning(f"Папка логов не найдена: {logs_path}")
        return 0

    cutoff_time = datetime.datetime.now() - datetime.timedelta(days=days)
    for item in pathlib.Path(logs_path).rglob("*"):
        try:
            mtime = datetime.datetime.fromtimestamp(item.stat().st_mtime)
            if mtime > cutoff_time:
                continue
            if dry_run:
                logger.info(f"[Dry Run] Будет удалено: {item}")
                continue
            if item.is_file():
                size = item.stat().st_size
                item.unlink()
                deleted_size += size
            elif item.is_dir():
                size = get_folder_size(item)
                shutil.rmtree(item, ignore_errors=True)
                deleted_size += size
            logger.info(f"Удалено: {item}")
        except Exception as e:
            logger.error(f"Ошибка при удалении {item}: {e}")

    size_after = get_folder_size(logs_path)
    logger.info(f"Очищено логов: {(size_before - size_after) / 1024 / 1024:.2f} MB")
    return deleted_size

def clean_recycle_bin(dry_run=False):
    """Очистка корзины."""
    logger.info("Начало очистки корзины")
    deleted_size = 0
    recycle_bin = r"C:\$Recycle.Bin"
    try:
        if dry_run:
            logger.info("[Dry Run] Корзина будет очищена")
            return 0
        if not os.path.exists(recycle_bin):
            logger.warning("Корзина не найдена")
            return 0
        size_before = get_folder_size(recycle_bin)
        subprocess.run(["rd", "/s", "/q", recycle_bin], shell=True, capture_output=True, text=True)
        size_after = get_folder_size(recycle_bin) if os.path.exists(recycle_bin) else 0
        deleted_size = size_before - size_after
        logger.info(f"Корзина очищена: {deleted_size / 1024 / 1024:.2f} MB")
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {e}")
    return deleted_size

def main():
    parser = ArgumentParser(description="Скрипт очистки мусора")
    parser.add_argument("--dry-run", action="store_true", help="Тестовый режим без удаления")
    args = parser.parse_args()

    logger.info("Запуск скрипта очистки")
    total_deleted = 0
    errors = []

    # Очистка кэша Яндекс.Браузера
    try:
        total_deleted += clean_yandex_browser_cache(dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Ошибка при очистке кэша Яндекс.Браузера: {e}")
        errors.append(str(e))

    # Очистка системных папок
    folders = [
        os.getenv("TEMP"),
        r"C:\Windows\Temp",
        r"C:\Windows\SoftwareDistribution\Download"
    ]
    for folder in folders:
        try:
            total_deleted += clean_system_folder(folder, dry_run=args.dry_run)
        except Exception as e:
            logger.error(f"Ошибка при очистке {folder}: {e}")
            errors.append(str(e))

    # Очистка логов старше 7 дней
    try:
        total_deleted += clean_old_logs(r"C:\Windows\Logs", dry_run=args.dry_run, days=7)
    except Exception as e:
        logger.error(f"Ошибка при очистке логов: {e}")
        errors.append(str(e))

    # Очистка корзины
    try:
        total_deleted += clean_recycle_bin(dry_run=args.dry_run)
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {e}")
        errors.append(str(e))

    # Отправка уведомления в Telegram
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    message = f"Очистка завершена. Освобождено: {total_deleted / 1024 / 1024:.2f} MB."
    if errors:
        message += f"\nОшибки: {', '.join(errors)}"
    if not args.dry_run and token and chat_id:
        asyncio.run(send_telegram_message(token, chat_id, message))
    elif not token or not chat_id:
        logger.warning("Telegram уведомления не отправлены: отсутствует токен или chat ID")

    logger.info(f"Очистка завершена. Освобождено: {total_deleted / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    main()