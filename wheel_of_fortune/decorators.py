import time
import logging

logging.basicConfig(filename='game.log', level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        mins, secs = divmod(int(elapsed), 60)
        print(f"Время игры: {mins} мин {secs} сек")
        return result
    return wrapper

def log_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"{type(e).__name__} - {e}")
            print(f"Произошла ошибка: {e}")
    return wrapper
