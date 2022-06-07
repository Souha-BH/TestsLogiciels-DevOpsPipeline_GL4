# Dockerfile
FROM python:3.9

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

CMD ["python3", "app/musician_application.py"]
