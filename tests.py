import unittest
import os
import pathlib
import datetime
import tempfile
import shutil
from cleanup import clean_yandex_browser_cache, clean_system_folder, clean_old_logs

class TestCleanupScript(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.cache_dir = os.path.join(self.test_dir, "Yandex", "YandexBrowser", "User Data", "Default")
        os.makedirs(self.cache_dir)
        self.logs_dir = os.path.join(self.test_dir, "Logs")
        os.makedirs(self.logs_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_yandex_browser_cache(self):
        cache_file = os.path.join(self.cache_dir, "cache.txt")
        cookies_file = os.path.join(self.cache_dir, "Cookies")
        with open(cache_file, "w") as f:
            f.write("test")
        with open(cookies_file, "w") as f:
            f.write("cookies")

        clean_yandex_browser_cache(dry_run=True, cache_path=self.cache_dir)
        self.assertTrue(os.path.exists(cookies_file), "Cookies должны остаться")
        clean_yandex_browser_cache(dry_run=False, cache_path=self.cache_dir)
        self.assertTrue(os.path.exists(cookies_file), "Cookies не должны удаляться")
        self.assertFalse(os.path.exists(cache_file), "Кэш должен быть удалён")

    def test_system_folder(self):
        test_file = os.path.join(self.test_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        clean_system_folder(self.test_dir, dry_run=False)
        self.assertFalse(os.path.exists(test_file), "Файл должен быть удалён")

    def test_old_logs(self):
        old_file = os.path.join(self.logs_dir, "old.log")
        new_file = os.path.join(self.logs_dir, "new.log")
        with open(old_file, "w") as f:
            f.write("old")
        with open(new_file, "w") as f:
            f.write("new")

        old_time = (datetime.datetime.now() - datetime.timedelta(days=10)).timestamp()
        os.utime(old_file, (old_time, old_time))

        clean_old_logs(self.logs_dir, days=7, dry_run=False)
        self.assertFalse(os.path.exists(old_file), "Старый лог должен быть удалён")
        self.assertTrue(os.path.exists(new_file), "Новый лог должен остаться")

if __name__ == "__main__":
    unittest.main()