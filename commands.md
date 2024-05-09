1.build docker image:

docker-compose up -d --build


2.run docker terminal:

docker exec -it django /bin/sh

## to see all env variables
docker exec -it django printenv


3.logs:

docker logs <container_name_or_id>
docker-compose logs


4.connecting redis container from django container to access the redis-cli:

redis-cli -h redis


5.checking the keys,type.values from redis-cli:

SCAN 0 MATCH *
TYPE key_name
HGETALL key_name

#clear all keys of redis
FLUSHDB


## to check the current celery broker connection

from celery import current_app
current_app.broker_connection()
<Connection: amqp://guest:**@localhost:5672// at 0x7fedc29a0e10>

## check logs for celery 

celery -A djcelery beat --loglevel=debug


## check network in docker 
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' celery-beat
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' redis

nc -zv redis 6379
ping -c 4 172.29.0.2(ip of other redis container)

