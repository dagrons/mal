FROM python:3.7.10-stretch

RUN apt update && apt install -y nasm &&\
    pip3 install torch torchvision

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt && chmod +x binary_requirements.sh &&\
    ./binary_requirements.sh

ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 FLASK_ENV=development

VOLUME /app

EXPOSE 5000

CMD flask run -h 0.0.0.0
