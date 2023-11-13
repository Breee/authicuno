FROM python:3.12-alpine

# Working directory for the application
WORKDIR /usr/src/app

COPY authicuno/requirements.txt /usr/src/app/requirements.txt

RUN apk --no-cache update && apk --no-cache upgrade && apk --no-cache add --virtual buildpack gcc musl-dev build-base
RUN apk --no-cache update && apk --no-cache add git

RUN cd /usr/src/app && python3 -m pip install -U -r requirements.txt

COPY authicuno /usr/src/app
RUN cp config.py.dist config.py

RUN apk del buildpack

ARG tag=0
ENV TAG=$tag

# Set Entrypoint with hard-coded options
ENTRYPOINT ["python3"]
CMD ["./start_bot.py"]

