# lifestream-utm

Связка lifestream и utm: удаление подписок у пользователей в lifestream в случае ухода в блок пользователя в utm.

## Установка

```
git clone https://github.com/ds-vologdin/lifestream-utm.git
cd lifestream-utm
virtualenv -p python3 env
pip install -r requirements.txt
```

Не забываем про файл private_settings.py. Пример файла можно посмотреть в private_settings.py.sample.

Настраиваем crontab
```
*/20 * * * * /full/path/to/lifestream-utm/lifestream.sh
```

# Docker

## сборка образа

```
docker build -t lilfestream:latest .
```

## запуск контейнера

```
docker run -it ds-vologdin/lilfestream:latest
```

# Docker-compose

```bash
docker-compose up
```

если нам надо предварительно собрать образ, то
```bash
docker-compose up --build
```

Логи будут лежать в /var/lib/docker/containers/[container-id]/[container-id]-json.log