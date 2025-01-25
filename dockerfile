FROM python:3.8


WORKDIR /code


COPY . /code


RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD [ "fastapi","run", "main:app", "--port", "8000" ]