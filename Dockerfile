FROM python:3.9-slim
WORKDIR /usr/src/ke-stat
COPY requirements.txt .

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .
# ENV VIRTUAL_ENV /env
# ENV PATH /env/bin:$PATH
#CMD ["python", "manage.py", "makemigrations"]
#CMD ["python", "manage.py", "migrate"]
EXPOSE 8080



CMD ["gunicorn", "--bind", ":8080", "--workers", "20", "market.wsgi:application"]
