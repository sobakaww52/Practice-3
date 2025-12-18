import linecache
import random
import os
import sys

def get_data_path():
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, 'data')

DATA_PATH = get_data_path()
WORDS_FILE = os.path.join(DATA_PATH, 'words.txt')
RECORD_FILE = os.path.join(DATA_PATH, 'record.txt')

def random_word_generator():
    used_lines = set()
    try:
        with open(WORDS_FILE, 'r', encoding='utf-8') as f:
            total_lines = sum(1 for _ in f)
    except FileNotFoundError:
        print("Ошибка: файл words.txt не найден!")
        return

    while len(used_lines) < total_lines:
        line_num = random.randint(1, total_lines)
        if line_num not in used_lines:
            used_lines.add(line_num)
            line = linecache.getline(WORDS_FILE, line_num)
            if line:
                yield line.strip()

def load_record():
    try:
        with open(RECORD_FILE, 'r', encoding='utf-8') as f:
            return int(f.read().strip())
    except (FileNotFoundError, ValueError):
        return 0

def save_record(record: int):
    try:
        os.makedirs(os.path.dirname(RECORD_FILE), exist_ok=True)
        with open(RECORD_FILE, 'w', encoding='utf-8') as f:
            f.write(str(record))
    except Exception as e:
        print(f"Ошибка записи рекорда: {e}")
