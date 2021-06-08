<p align="left">
  <img src=img/spamy.png height=300>
  <p align="left">
	<a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/runs%20on-python-brightgreen" />
      </a>
	<a href="https://www.sqlite.org/index.html">
	  <img src="https://img.shields.io/badge/runs%20on-sqlite3-brightgreen">
      </a>
  <a href="https://telegram.org">
	  <img src="https://img.shields.io/badge/runs%20on-telegram-9cf">
      </a>
  </p>
</p>

# Spamy telegram bot
[**@spamy_teleg_bot**](https://t.me/spamy_teleg_bot)  

Бот является интерфейсом к базе данных с хранением отзывов пользователей о негативном опыте звонков от конкретных телефонных номеров. Цель бота - предоставить возможность людям делиться номерами злоумышленников, чтобы предостеречь от контактов с ними.

## DataBase:
<img src=pageimg/database_structure.jpg height=300>
База данных находится в 3й нормальной форме, так как все неключевые столбцы зависят только от первичного ключа.  

## Inreface:
* поиск информации по номеру теофона
* идентификация пользователя по `TelegramID`
* добавлние отзывов с указанием категории и комментария
* поиск всех отзывов пользователя
* изменение написанных отзывов
* удаление написанных отзывов

[**видео с демонстрацией**](https://drive.google.com/file/d/1zi7y3rADAkPo8A45RJ9imYq9g6yjyQyt/view?usp=drivesdk)
