# Deutsch Begegnungen A2/B1 для Anki

Цей проєкт збирає Anki-колоду `Deutsch_Begegnungen_A2_B1` для вивчення німецької з українськими перекладами. Картки містять словникову форму, граматичні дані, форми дієслів і до двох прикладів із перекладом.

Після збірки імпортуйте `Deutsch_Begegnungen_A2_B1.apkg` через меню **File → Import** в Anki Desktop або відкрийте файл в AnkiMobile чи AnkiDroid.

## Що потрібно

- Python 3.9 або новіший;
- `pip`;
- пакет `genanki`, версію якого зафіксовано в `requirements.txt`;
- Anki лише для використання готової колоди. Для збірки `.apkg` Anki не потрібен.

Скрипти використовують переносимі API Python і працюють у Linux, macOS та Windows.

## Встановлення

### Linux і macOS

```bash
git clone <repository-url>
cd anki_cards
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### Windows PowerShell

```powershell
git clone <repository-url>
Set-Location anki_cards
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Якщо PowerShell забороняє запуск локального сценарію активації, виконайте команди через `cmd.exe` або дозвольте локальні підписані сценарії згідно з політикою вашої системи.

## Збірка колоди

```bash
python build_apkg.py
```

Скрипт перевірить усі записи у `words.json`, зупиниться на помилковій структурі чи дублікаті та створить у корені проєкту файл `Deutsch_Begegnungen_A2_B1.apkg`.

Без створення віртуального середовища колоду можна зібрати через [uv](https://docs.astral.sh/uv/):

```bash
uv run --no-project --with genanki==0.13.1 python build_apkg.py
```

## Структура даних

`words.json` є єдиним актуальним джерелом карток. Кожен запис має п'ять полів у фіксованому порядку:

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

Символ `*` позначає межу відокремлюваного префікса. Генератор не показує його в TTS-полі. Стабільні ID колоди, моделі й нотаток дозволяють повторно імпортувати нову версію `.apkg` без створення копій карток.

## Додавання карток

Підготуйте JSON-масив нових записів у тимчасовому файлі. Не редагуйте наявні записи в `words.json`, якщо ви лише додаєте матеріал.

Спочатку перевірте файл без змін у колоді:

```bash
python merge_words.py --dry-run /path/to/candidates.json
```

У Windows передайте звичайний Windows-шлях, наприклад `C:\Temp\candidates.json`.

Після успішної перевірки додайте записи й перебудуйте пакет:

```bash
python merge_words.py /path/to/candidates.json
python build_apkg.py
```

`merge_words.py` перевіряє схему, пропускає дублікати та дописує нові картки в кінець масиву.

## Черга зображень

Каталог `Words/` призначений для локальних зображень зі словами. Його вміст не потрапляє до Git, оскільки скриншоти можуть містити персональні або захищені авторським правом матеріали.

Переглянути нові чи змінені файли:

```bash
python image_queue.py pending
```

Після розпізнавання, перевірки, злиття карток і успішної збірки позначте зображення як опрацьовані:

```bash
python image_queue.py mark "Words/example.png"
```

Скрипт зберігає локальні checksum і час обробки в `image_import_state.json`. Git ігнорує цей файл. Проєкт не містить OCR: текст із зображень потрібно розпізнати окремим інструментом і перевірити вручну.

## Файли проєкту

- `build_apkg.py` створює пакет Anki;
- `merge_words.py` перевіряє та додає нові записи;
- `word_utils.py` містить спільну валідацію й нормалізацію;
- `image_queue.py` керує локальною чергою зображень;
- `words.json` зберігає картки;
- `Deutsch_Begegnungen_A2_B1.apkg` є локальним результатом збірки.

Каталоги `Words/`, `backups/`, згенерований пакет `.apkg`, локальний стан імпорту, секрети, кеші Python та налаштування редакторів виключено з репозиторію через `.gitignore`.
