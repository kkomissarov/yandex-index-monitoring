# Сравнение проиндексированных яндексом страниц и карты сайта

## Зависимости
- >=python3.7 

## Установка
1. Установить зависимости
```pip install -r requirements.txt```

2. Скопировать config_sample.py в config.py:

```cp config_sample.py config.py```

3. Скопировать config_sample.xlsx в config.xlsx:

```cp config_sample.xlsx config.xlsx```

4. Заполнить переменные конфигурации:

TOKEN - токен API Яндекса
SITES_LIST_PATH - Путь до файла, в котором хранится список сайтов (по-умолчанию config.xlsx)

YANDEX_PER_REQUEST_PAGE_LIMIT - Сколько страниц в индексе возвращать в одном запросе к Яндекс.API (макс. 100)

VISUAL_REPORTS_DIR - Директория, в которой будут создаваться визуальные отчеты

RECRAWL_BASES_DIR - Директория, в которой будут создаваться файлы со списком страниц для переобхода

VISUAL_REPORT_FILENAME_TEMPLATE = Шаблон названия файла визуалного отчета (по-умолчанию '{project_name}_{current_date}.xlsx', можно использовать переменные project_name и current_date)

5. Добавить сайты в файл config.xlsx по образцу


## Запуск
```python3 main.py```