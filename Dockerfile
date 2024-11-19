# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Указываем порт, на котором приложение будет работать
EXPOSE 5006

# Запускаем приложение
CMD ["python", "docsend/flask_service.py"]
