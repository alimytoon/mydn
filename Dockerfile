FROM eclipse-temurin:21-jre-alpine

RUN apk add --no-cache python3 py3-pip py3-flask bash curl wget

WORKDIR /app
COPY . /app

RUN mkdir -p /data && \
    wget -O /data/server.jar https://api.papermc.io/v2/projects/paper/versions/1.20.4/builds/497/downloads/paper-1.20.4-497.jar

EXPOSE 8080 25565

CMD ["python3", "main.py"]
