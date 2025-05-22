FROM python:3.10

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations \
                   && python manage.py migrate \
                   && python manage.py collectstatic --noinput \
                   && python manage.py init_ingridients \
                   && gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000"]
