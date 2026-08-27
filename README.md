# Anki Deutsch: Begegnungen A2/B1

Проєкт створює Anki-колоду `Deutsch_Begegnungen_A2_B1` для вивчення німецької з українськими перекладами. Картки містять словникову форму, граматичні дані, форми дієслів і до двох прикладів із перекладом.

`words.json` зберігає вихідні дані колоди. Скрипт `build_apkg.py` перевіряє ці дані та створює `Deutsch_Begegnungen_A2_B1.apkg`. Git не відстежує згенерований пакет, тому після клонування його потрібно зібрати локально.

## Вимоги

- Python 3.9 або новіший;
- `pip`;
- Anki Desktop, AnkiMobile або AnkiDroid для імпорту готової колоди.

Для збірки потрібен лише Python і залежності з `requirements.txt`. Встановлювати Anki на комп'ютер зі скриптами не потрібно.

## Встановлення

### Linux і macOS

```bash
git clone https://github.com/Konstantin212/anki_cards.git
cd anki_cards
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
git clone https://github.com/Konstantin212/anki_cards.git
Set-Location anki_cards
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Якщо PowerShell блокує сценарій активації, активуйте середовище через `cmd.exe` або змініть політику виконання лише для поточного сеансу.

## Збірка та імпорт

Створіть пакет:

```bash
python build_apkg.py
```

Успішна команда завершується повідомленням:

```text
Wrote .../Deutsch_Begegnungen_A2_B1.apkg (N notes)
```

Скрипт зупинить збірку, якщо `words.json` містить неправильну структуру або дублікат. Після успішної збірки імпортуйте `Deutsch_Begegnungen_A2_B1.apkg` через **File → Import** в Anki Desktop або відкрийте файл в AnkiMobile чи AnkiDroid.

Фіксовані ID колоди й моделі та стабільні GUID нотаток дозволяють імпортувати оновлену версію пакета без створення копій карток.

### Збірка через uv

Якщо ви використовуєте [uv](https://docs.astral.sh/uv/), віртуальне середовище створювати не потрібно:

```bash
uv run --no-project --with genanki==0.13.1 python build_apkg.py
```

## Формат картки

Кожен елемент `words.json` має п'ять полів у фіксованому порядку:

```json
{
  "word": "auf*stehen",
  "full": "",
  "translation": "вставати",
  "forms": "Perfekt: er ist aufgestanden · Präteritum: er stand auf",
  "examples": [
    [
      "Ich stehe jeden Tag um sieben Uhr auf.",
      "Я щодня встаю о сьомій годині."
    ]
  ]
}
```

- `word`: словникова форма без артикля; `*` позначає межу відокремлюваного префікса;
- `full`: артикль, іменник і форма множини;
- `translation`: короткий переклад українською;
- `forms`: Perfekt і Präteritum для дієслова;
- `examples`: від нуля до двох пар німецького й українського речень.

## Додавання карток

Підготуйте JSON-масив нових записів у файлі поза репозиторієм. Спочатку запустіть перевірку без зміни `words.json`:

```bash
python merge_words.py --dry-run /path/to/candidates.json
```

У Windows використовуйте Windows-шлях, наприклад `C:\Temp\candidates.json`.

Перегляньте рядки `ADD` і `SKIP`. Якщо перевірка пройшла, додайте записи й перебудуйте пакет:

```bash
python merge_words.py /path/to/candidates.json
python build_apkg.py
```

`merge_words.py` перевіряє схему, пропускає дублікати та додає нові картки в кінець масиву.

## Черга зображень

Зберігайте локальні зображення зі словами в `Words/`. Git ігнорує вміст цього каталогу, оскільки скриншоти можуть містити персональні дані або матеріали, захищені авторським правом.

Перегляньте нові чи змінені файли:

```bash
python image_queue.py pending
```

Проєкт не виконує OCR. Розпізнайте текст окремим інструментом, перевірте результат за зображенням і додайте картки через `merge_words.py`.

Після успішного злиття та збірки позначте зображення як опрацьоване:

```bash
python image_queue.py mark "Words/example.png"
```

`image_queue.py` зберігає контрольні суми й час обробки в локальному `image_import_state.json`. Git ігнорує цей файл.

## Структура репозиторію

- `words.json`: єдине актуальне джерело карток;
- `build_apkg.py`: перевірка даних і створення пакета Anki;
- `merge_words.py`: перевірка та додавання нових записів;
- `word_utils.py`: спільна валідація, нормалізація й атомарний запис JSON;
- `image_queue.py`: черга локальних зображень;
- `requirements.txt`: зафіксована версія `genanki`;
- `.github/workflows/build.yml`: перевірка збірки на Linux, macOS і Windows з Python 3.9 та 3.13.

## Локальні файли

`.gitignore` виключає з репозиторію:

- згенерований `Deutsch_Begegnungen_A2_B1.apkg`;
- зображення в `Words/`;
- резервні копії в `backups/`;
- локальні ресерчі та робочі нотатки;
- `image_import_state.json`, кеші Python, секрети й налаштування редакторів.

Ці файли залишаються на вашому комп'ютері й не потрапляють до комітів.
