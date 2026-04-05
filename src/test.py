try:
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    print("Файл прочитан успешно в UTF-8!")
except UnicodeDecodeError:
    print("Ошибка: Файл НЕ в кодировке UTF-8 или содержит битые символы.")