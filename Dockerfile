FROM python:3.9-slim-buster

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY bot.py /

CMD ["python3", "bot.py"]
