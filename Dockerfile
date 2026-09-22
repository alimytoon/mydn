FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache python3 py3-pip py3-flask bash curl wget

WORKDIR /app
COPY . /app

RUN mkdir -p /data

EXPOSE 8080 25565

CMD ["python3", "main.py"]
