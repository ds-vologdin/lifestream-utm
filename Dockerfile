FROM python:3.7-alpine

RUN addgroup -S lifestream && adduser -S -G lifestream lifestream
RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=lifestream:lifestream . .

USER lifestream:lifestream
ENTRYPOINT ["python", "lifestream-utm/lifestream.py", "--log-level=info", "--email-report=bud_on@kirovcity.ru i.solovyev@kgts.su"]