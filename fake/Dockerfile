FROM python:alpine3.20

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY project project

ENV FLASK_APP=project/main.py
ENV FLASK_DEBUG=1

CMD ["python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5099"]
