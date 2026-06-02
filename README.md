# ⚡ pseudogen — Pseudocode && Blockscheme Generator

Автоматизированный конвейер для студентов, превращающий исходный код в идеальные блок-схемы строго по **ГОСТ 19.701-90** и чистый псевдокод. Больше никакой ручной отрисовки стрелочек в Visio или Draw.io. Генерируй схемы в один клик и получай свои заслуженные 9 и 10 на лабах!

---

## 🔥 Фичи

* **Полная всеядность**: Автоматически распознает и парсит файлы на **C++** (`.cpp`, `.hpp`) и **Python** (`.py`).
* **Тотальный клининг текста**: Вырезает плюсовый и питонячий мусор (`int main()`, `std::`, `endl`, `;`).
* **ГОСТ-оформление**: Автоматически форматирует ввод/вывод в стиле `Ввод: ...` / `Вывод: ...`, разворачивает инкременты (`i++` -> `i = i + 1`) и ставит красивые математические знаки (`×`, `÷`, `≠`).

---

## 🛠 Установка и Запуск

```bash
git clone https://github.com/sc0dyx/pseudogen.git
cd pseudogen
pip install -e .
```

### 1. Генерация текстового псевдокода

```bash
pseudogen -i input.cpp -g default.pgen -o output.txt -t pseudocode
```

### 2. Генерация ГОСТ блок-схемы (JSON)

```bash
pseudogen -i лаба.cpp -o schema.json -t blockscheme
```

*(Для Python-файлов просто скорми `.py` вместо `.cpp` — скрипт сам переключит парсер под капотом).*

---

## 🚀 Как получить готовую картинку?

1. Сгенерируй JSON-файл схемы с помощью команды выше.
2. Зайди на сайт: [Редактор блок-схем programforyou.ru](https://programforyou.ru/block-diagram-redactor)
3. И загрузи свой JSON.
4. Забирай идеальную схему со стрелочками!

---

## Пример

Написал я вот такой код на С++

```cpp
#include <iostream>

int main(){
  std::cout << "Начало счетчика" << std::endl;
  for (int i = 0; i < 10; i++){
    std::cout << i << std::endl;
  }
  std::cout << "Конец счётчика" << std::endl;
  return 0;
}
```

файл назвал example.cpp

```bash
 ⚙  scodyx@localhost  ~/git/pseudogen   main  python3 -m src.pseudogen -i example.cpp -o output.json -t blockscheme   

[C++] Diagram has been saved as output.json
Upload it here: https://programforyou.ru/block-diagram-redactor
 ⚙  scodyx@localhost  ~/git/pseudogen   main 
```

теперь загружаем файл output.json на сайт

<img width="216" height="49" alt="image" src="https://github.com/user-attachments/assets/29fe31f8-df32-46bd-a020-548ba350b176" />

и вот результат

<img width="1280" height="720" alt="pseudogen_demo" src="https://github.com/user-attachments/assets/25455676-be54-4754-a8d7-6f044be55523" />

---

## 🏛 Credits & Благодарности

Проект вобрал в себя лучшие идеи из заброшенных студенческих репозиториев и взлетел благодаря кодовой базе истинного мастера кодинга:

1. **GachiLord (ГачиЛорд)** — настоящий Dungeon Master статического анализа. Спасибо ему за базовую логику парсинга, реализованную в проектах [Python2FlowChart](https://github.com/GachiLord/Python2FlowChart) и [PyChart](https://github.com/GachiLord/PyChart). Оригинальный код перенёс суровый fisting со стороны Python 3, был полностью очищен от багов с импортами, избавлен от циклического наследования и адаптирован под монолитную архитектуру. Boy Next Door одобряет! ♂️ 👑

---
Сделано студентом для студентов. Пользуйтесь, кайфуйте и закрывайте дедлайны по щелчку пальцев! 🍻

<sup>*Планируем переписать python код на С++ (скоро ... )*</sup>
