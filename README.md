Лабораторная работа по сетевому программированию Интернет магазин

Для работы необзодимо:
- python 2.x
- postgres
- библиотеки из файла requirements.txt

Развертывание:

Скопировать проект на локальную мащину:
- git clone https://github.com/SkyInEyes/social_networking.git

Если есть pip:
- pip install -r requirments.txt

Если нету pip:
- Установить все необходимые пакеты из файла requirments.txt

Восстановить базу данных на локальной машине:

- psql -U test_db < shop_db_dump (password: blitzcrank)

Запустить сервер на локальной машине:
- python manage.py runserver
