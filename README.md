<div align="center">
  <h1>🐭 Джерри и сырное воздаяние 🧀 </h1>
  <h3><i>2D‑платформер на pygame</i></h3>
  <q><i>Нет сыра🧀 без огня🔥</i></q>
  <br>
  <br>

  <!-- Стек -->
  <img src="https://img.shields.io/badge/Engine-Pygame_CE-3776AB?logo=python&logoColor=white" alt="Pygame CE" title="Движок">
  <img src="https://img.shields.io/badge/Language-Python_3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-yellow?logo=opensourceinitiative&logoColor=white" alt="Лицензия MIT">
  <br>
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?logo=github" alt="Статус проекта">
  <img src="https://img.shields.io/badge/Platform-Windows_|_Linux_|_macOS-lightgrey?logo=windows&logoColor=white" alt="Платформы">
  <img src="https://img.shields.io/badge/Resolution-1280x720-blueviolet?logo=display&logoColor=white" alt="Разрешение">
</div>

---

## 📖 Джерри и сырное воздаяние - это...

...2D‑платформер с видом сбоку, вдохновлённый мультом "Том и Джерри".
Игрок почувствует себя в шкуре **Джерри**, который сталкивается с **аркадными уровнями**, **боссфайтом** и **вкусным сырком**.

> **Цель игры** - собрать весь сыр на уровне и [найти выход](https://vk.com/naitivihod), избегая встречи с **котом Томом**, его приспешниками и мышеловками.

---

## ✨ Особенности

<table>
  <tr>
    <th>Gameplay</th>
    <td>
      - камера с эффектом следования;<br>
      - толкаемые ящики, кусающиеся мышеловки, движущиеся платформы;<br>
      - система здоровья и "шкала сыра" (восстановления при сборе сыра).
    </td>
  </tr>
  <tr>
    <th>AI</th>
    <td>
      - патрулирование Врагов по заданным маршрутам;<br>
      - преследование Игрока при обнаружении;<br>
      - паузы и возврат к патрулированию при потере цели.
    </td>
  </tr>
  <tr>
    <th>VFX</th>
    <td>
      - параллакс-эффект для фонов;<br>
      - анимированные спрайты персонажей и объектов.
    </td>
  </tr>
  <tr>
    <th>SFX</th>
    <td>
      - настройка громкости музыки и SFX.
    </td>
  </tr>
</table>

---

## 🚀 Установка и запуск

### Для обычных пользователей

<details>
<summary><b>📦 Готовые сборки (в разработке)</b></summary>
<br>
В ближайшее время здесь появятся ссылки на скомпилированные исполняемые файлы <code>.exe</code> для Windows.  
Пока вы можете запустить игру как разработчик (инструкция ниже).
</details>

### Для разработчиков

#### 📋 Требования

- **Python** версии `3.10` или выше;
- рекомендуется использовать **виртуальное окружение**.

#### 🔧 Пошаговая установка

1. **Клонируйте репозиторий:**

   ```bash
   git clone https://github.com/MindlessMuse666/tom-i-jerry.git
   cd tom-i-jerry
   ```

2. **Создайте и активируйте виртуальное окружение (опционально):**

   ```bash
   py -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Linux/macOS:
   source .venv/bin/activate
   ```

3. **Установите зависимости:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Запустите игру:**

   ```bash
   py main.py
   ```

---

## 🎮 Управление

| Действие                 | Клавиша            |
| ------------------------ | ------------------ |
| Движение влево / вправо  |  `A` `D` или `СТРЕЛКА_ВЛЕВО` `СТРЕЛКА_НАПРАВО` |
| Прыжок                   | `Пробел` или `W`           |
| Пауза / Меню             | `Esc`              |
<!-- Шумовая приманка             | `ЛКМ` или `F`              | -->

*Управление можно настроить в будущих версиях.*

---

## 📁 Структура проекта

```
project_root/
├───main.py                 # Точка входа, основной цикл
├───setting.py              # Общие настройки игры (экран, FPS, громкость по умолчанию)
├───constant.py             # Константы (цвета, пути, идентификаторы)
│
├───config/                 # Конфиги сущностей
│       player.toml
│       enemy.toml
│       boss.toml
│       level.toml
│
├───core/                   # Ядро движка
│       game.py               # Управление сценами, главный цикл
│       state_machine.py      # Базовая state machine
│       camera.py             # Камера
│       resource.py           # Загрузка и кэширование ресурсов
│       mixer.py              # Управление звуком с фейдами и полифонией
│
├───scene/                  # Сцены (экраны)
│       base.py
│       menu.py
│       level.py
│       pause.py
│       victory.py
│
├───entity/                 # Игровые сущности (спрайты)
│       player.py
│       cheese.py
│       crate.py
│       trap.py
│       broom.py
│       tom.py
│       boss.py
│       projectile.py       # Ракета, шумовая приманка
│
├───ui/                     # Элементы UI
│       hud.py
│       button.py
│       slider.py
│
├───level/                  # Данные уровней (JSON/TMX)
│       level1.json
│       level2.json
│       level3.json
│
└───asset/                  # Все ресурсы (уже загружены)
    ├───visual/
    │   ├───entity/
    │   └───ui/
    ├───font/
    └───audio/
        ├───music/
        └───sfx/
├──requirements.txt         # Зависимости проекта
└──README.md                # Этот файл
```

---

## 📄 Лицензия

Этот проект распространяется под лицензией **MIT**.  
Подробности смотрите в файле [LICENSE](LICENSE).

---

## 👤 Автор

<div align="center">
  <a href="https://github.com/MindlessMuse666" target="_blank">
    <img src="https://github.com/MindlessMuse666.png" width="80" style="border-radius: 50%;" alt="Влад" title="Сырная власть">
  </a>
  <br>
  <b>Влад</b> (<i>MindlessMuse666</i>)
  <br>
  <sub>Dev, GameDesign, SoundDesign, СырнаяВласть</sub>
  <br><br>
  <a href="https://github.com/MindlessMuse666/tom-i-jerry" target="_blank">🔗 Репо проекта</a>
</div>

<br>

> 📚 **Учебная практика** - проект создан в рамках учебной практики в колледже, цель которой - освоить принципы разработки 2D‑игр, работу с движком и создание геймплея на Python.

---

<div align="center">
  <sub>© 2025 <a href="https://github.com/MindlessMuse666" target="_blank">MindlessMuse666</a> · Джерри и сырное воздаяние</sub>
  <br>
  <sup><i>“Разработано с любовью к сыру 🧀”</i></sup>
</div>
