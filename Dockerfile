# Dockerfile
FROM python:3.9

ADD musician_application.py .

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt 

CMD [ "python3", "musician_application.py"]
