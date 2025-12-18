import logging
from datetime import datetime
from .file_handler import random_word_generator, load_record, save_record, WORDS_FILE
from .decorators import timer, log_errors
from .utils import mask_word, hearts
import linecache
import os


# Настройка логирования в файл
LOG_FILE = "game.log"


# Создаем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Удаляем все существующие обработчики
logger.handlers.clear()


# Создаем обработчик для записи в файл
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.INFO)


# Форматтер для логов
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', 
                              datefmt='%Y-%m-%d %H:%M:%S')
file_handler.setFormatter(formatter)


# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


# Отключаем вывод логов в консоль через корневой логгер
logging.getLogger().setLevel(logging.WARNING)
for handler in logging.getLogger().handlers:
    if isinstance(handler, logging.StreamHandler):
        logging.getLogger().removeHandler(handler)



@log_errors
@timer
def start_game():
    """Запуск игры Поле Чудес"""
    game_session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"=== НАЧАЛО ИГРЫ === Сессия: {game_session_id}")
    print("=== ПОЛЕ ЧУДЕС ===")
    
    record = load_record()
    logger.info(f"Загружен рекорд: {record} слов")
    print(f"🏆 Ваш лучший рекорд: {record} слов")

    levels = {'1': 7, '2': 5, '3': 3}
    while True:
        level = input(
            "Выберите уровень сложности:\n"
            "1. Легкий (7 жизней)\n"
            "2. Средний (5 жизней)\n"
            "3. Сложный (3 жизни)\n"
            "Ваш выбор: "
        ).strip()
        
        if level in levels:
            lives_start = levels[level]
            level_name = {1: "Легкий", 2: "Средний", 3: "Сложный"}[int(level)]
            logger.info(f"Выбран уровень сложности: {level_name} ({lives_start} жизней)")
            break
        logger.warning(f"Некорректный выбор уровня: '{level}'")
        print("Некорректный ввод, попробуйте еще раз.")

    words_gen = random_word_generator()
    guessed_count = 0

    try:
        with open(WORDS_FILE, encoding="utf-8") as f:
            total_words = sum(1 for _ in f)
        logger.info(f"Загружен файл со словами. Всего слов: {total_words}")
    except FileNotFoundError as e:
        logger.error(f"Файл со словами не найден: {WORDS_FILE}. Ошибка: {str(e)}")
        print("Файл со словами не найден. Игра невозможна.")
        return

    for word_index, word in enumerate(words_gen, start=1):
        logger.info(f"Начало слова #{word_index}: '{word}' (длина: {len(word)} букв)")
        guessed_letters = set()
        lives = lives_start

        print(f"\nСлово №{word_index} из {total_words}")
        print(mask_word(word, guessed_letters))
        print(f"Количество жизней: {hearts(lives)}")

        game_over = False
        while lives > 0 and not game_over:
            guess = input("Назовите букву или слово целиком: ").lower().strip()
            logger.info(f"Пользователь ввел: '{guess}' (осталось жизней: {lives})")

            if not guess.isalpha():
                logger.warning(f"Некорректный ввод (не буквы): '{guess}'")
                print("Ошибка: вводите только буквы.")
                continue

            if len(guess) > 1:
                if guess == word:
                    logger.info(f"Слово угадано целиком: '{word}'")
                    print("Вы угадали слово целиком!")
                    guessed_count += 1
                    game_over = True
                    break
                else:
                    logger.info(f"Неверное слово целиком: '{guess}' вместо '{word}'")
                    print("💔 ИГРА ОКОНЧЕНА! 💔")
                    print("Вы неверно назвали слово.")
                    print(f"Загаданное слово было: {word.upper()}")
                    end_game(guessed_count, total_words, record)
                    return

            if len(guess) == 1:
                if guess in word:
                    if guess in guessed_letters:
                        logger.debug(f"Повторная буква: '{guess}'")
                        print("Эту букву вы уже называли.")
                        continue

                    guessed_letters.add(guess)
                    logger.info(f"Угадана буква: '{guess}'")
                    masked = mask_word(word, guessed_letters)
                    print(masked)
                    
                    # Логируем прогресс
                    guessed_letters_in_word = [c for c in word if c in guessed_letters]
                    logger.info(f"Прогресс слова: {len(guessed_letters_in_word)}/{len(word)} букв - {', '.join(sorted(guessed_letters_in_word))}")

                    if masked == word:
                        logger.info(f"Слово полностью угадано: '{word}'")
                        print("Вы полностью открыли слово!")
                        guessed_count += 1
                        game_over = True
                        break
                    else:
                        print(f"Количество жизней: {hearts(lives)}")
                else:
                    lives -= 1
                    logger.info(f"Неверная буква: '{guess}', осталось жизней: {lives}")
                    print(f'Буквы "{guess}" нет в слове.')
                    print(f"Количество жизней: {hearts(lives)}")

        if lives == 0:
            logger.info(f"Закончились жизни для слова: '{word}'. Угадано букв: {len(guessed_letters)}")
            print("💔 ИГРА ОКОНЧЕНА! 💔")
            print("У вас закончились жизни.")
            print(f"Загаданное слово было: {word.upper()}")
            end_game(guessed_count, total_words, record)
            return

        # Если слово угадали успешно, переходим к следующему без вопроса
        if word_index < total_words:
            print("\n" + "="*50)  # Разделитель между словами
            continue
        else:
            # Все слова пройдены
            logger.info("Все слова в файле пройдены успешно")
            print("\n🎉 ПОЗДРАВЛЯЕМ! 🎉")
            print(f"Вы прошли всю игру и угадали все {total_words} слов(а)!")
            end_game(guessed_count, total_words, record)
            return

    # Если пользователь завершил игру досрочно
    end_game(guessed_count, total_words, record)


def end_game(guessed_count: int, total_words: int, record: int) -> None:
    """Завершение игры и вывод статистики"""
    logger.info(f"=== ЗАВЕРШЕНИЕ ИГРЫ === Угадано слов: {guessed_count}/{total_words}")
    
    print("\n📊 Ваша статистика:")
    print(f"Угадано слов: {guessed_count} из {total_words}")
    
    success_rate = (guessed_count / total_words * 100) if total_words > 0 else 0
    logger.info(f"Процент угаданных слов: {success_rate:.1f}%")
    logger.info(f"Угадано слов: {guessed_count}, Всего слов: {total_words}, Рекорд: {record}")

    if guessed_count > record:
        logger.info(f"УСТАНОВЛЕН НОВЫЙ РЕКОРД: {guessed_count} (предыдущий: {record})")
        print("🎊 НОВЫЙ РЕКОРД! 🎊")
        print(f"Предыдущий рекорд: {record} слов")
        print(f"Новый рекорд: {guessed_count} слов")
        save_record(guessed_count)
    else:
        logger.info(f"Рекорд не побит. Текущий результат: {guessed_count}, рекорд: {record}")
        print(f"Ваш лучший рекорд: {record} слов")

    linecache.clearcache()
    logger.info("Кэш очищен")
    
    # Логируем время завершения игры
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"Игра завершена в {end_time}")
    logger.info("=" * 50)  # Разделитель между сессиями
    
    print("\n=== ИГРА ЗАВЕРШЕНА ===")
    print("Хотите сыграть заново? (да/нет): ", end="")
    play_again = input().lower().strip()
    
    if play_again == "да":
        logger.info("Пользователь решил сыграть заново")
        start_game()
    else:
        logger.info("Пользователь завершил игру")
        print("Спасибо за игру!")
        print("\nНажмите Enter, чтобы выйти...")
        input()
