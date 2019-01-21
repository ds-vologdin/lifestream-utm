#!/usr/bin/env bash

cd `dirname $0`
source venv/bin/activate
python lifestream-utm/lifestream.py --log-level info  --email-report 'bud_on@kirovcity.ru i.solovyev@kgts.su' --log-file /var/log/lifestream.log
