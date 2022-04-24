FROM python:3.8-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY img/*.jpeg ./img/
COPY ./*.py ./

EXPOSE 5000

CMD ["python", "server.py"]
