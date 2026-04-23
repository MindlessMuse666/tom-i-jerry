<div align="center">
  <h1>🐭 Джерри и сырное воздаяние 🧀</h1>
  <h3><i>2d‑платформер на pygame</i></h3>
  <q><i>Нет сыра🧀 без огня🔥</i></q>
  <br>
  <br>

  <!-- Стек -->
  <img src="https://img.shields.io/badge/Engine-Pygame_CE-3776AB?logo=python&logoColor=white" alt="Pygame CE" title="Движок">
  <img src="https://img.shields.io/badge/Language-Python_3.10+-blue?logo=python&logoColor=white" alt="Python 3.10+">
  <img src="https://img.shields.io/badge/License-MIT-yellow?logo=opensourceinitiative&logoColor=white" alt="Лицензия MIT">
  <br>
  <img src="https://img.shields.io/badge/Status-Refactored-blue?logo=github" alt="Статус проекта">
</div>

---

## 📖 Джерри и сырное воздаяние - это...

...2D‑платформер с видом сбоку, вдохновлённый мультом "Том и Джерри".
Игрок почувствует себя в шкуре **Джерри**, который сталкивается с **аркадными уровнями**, **боссфайтом** и **вкусным сырком**.

> **Цель игры** - собрать весь сыр на уровне и [найти выход](https://vk.com/naitivihod), избегая встречи с **котом Томом**, няшными Мётлами и алюминиевыми мышеловками.

---

## ✨ Особенности

- **Динамическая камера**: Мув за Игроком + эффект взгляда в сторону курсора;
- **Интерактивщина**: Ящики, Капканы, Движущиеся платформы;
- **Шумовки**: Отвлекалка для врагов;
- **Боссфайт**: Тома в экзоскелете xd;
- **Мультимедиа**: Самым усердным Игрокам споёт Микуша;
- **Чит-коды**: Не дебаг, а фича.

---

## 🚀 Установка и запуск

### Для пользователей (Windows)

1. Скачайте последнюю версию из раздела [Releases](https://github.com/MindlessMuse666/tom-i-jerry/releases).
2. Запустите файл `SirnoeVozdayanie.exe`.  

### Для разработчиков

1. **Клонируйте репозиторий:**

  ```bash
  git clone https://github.com/MindlessMuse666/tom-i-jerry.git
  cd tom-i-jerry
  ```

2. **Настройте окружение (рекомендуется venv):**

  ```bash
  py -m venv .venv
  .venv\Scripts\activate
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

| Действие | Клавиша |
| -------- | ------- |
| **Движение** | `A` `D` или `←` `→` |
| **Прыжок** | `Пробел` или `W` / `↑` |
| **Приманка** | `ЛКМ` или `F` |
| **Пауза** | `Esc` |
| **Координаты (Чит)** | `8888` |
| **Бессмертие (Чит)** | `0000` |
| **Скип уровня (Чит)** | `9999` |

---

## 📂 Структура проекта

```text
tom-i-jerry/
├── asset/          # медиа: спрайты, sfx, ost, курсоры, шрифт
├── config/         # toml-конфиги: игрок, враги
├── core/           # ядро: ресурсы, микшер, камера, машина состояний
├── entity/         # игровые сущности: игрок, враги, окружение, снаряды
├── level/          # разметка уровней
├── scene/          # сцены: меню, уровни, настройки, титры
├── ui/             # ui: кнопки, слайдеры, HUD
├── constant.py     # Консты и пути
└── main.py         # Точка входа
```

---

## 🛠 Техническая документация

Подробное описание архитектуры, паттернов и систем игры доступно в файле [tech.md](doc/tech.md).

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

> 📚 **Учебная практика** - проект создан в рамках учебной практики в колледже, цель которой - освоить принципы разработки 2D‑игр, работу с движком.

---

<div align="center">
  <sub>© 2026 <a href="https://github.com/MindlessMuse666" target="_blank">MindlessMuse666</a> · Джерри и сырное воздаяние</sub>
  <br>
  <sup><i>“Разработано с любовью к сыру 🧀”</i></sup>
</div>
