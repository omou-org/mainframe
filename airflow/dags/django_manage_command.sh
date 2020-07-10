#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE="mainframe.settings.local"

cd /Users/jerry/robinhood/mainframe && python manage.py {{ params.command }}
