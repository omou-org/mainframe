from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(year=2020, month=7, day=1),
    'email': ['jerrylinew@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'send_session_reminders',
    default_args=default_args,
    description='Checks for upcoming sessions and send reminder emails to parents and instructors.',
    schedule_interval=timedelta(days=1),
)

send_session_reminders = BashOperator(
    task_id='send_session_reminders',
    bash_command="""
    export DJANGO_ENV_MODULE="mainframe.settings.local"; 
    cd /Users/jerry/robinhood/mainframe;
    python manage.py send_session_reminders; 
    """,
    dag=dag,
)

sleep = BashOperator(
    task_id='sleep',
    depends_on_past=False,
    bash_command='sleep 5',
    retries=3,
    dag=dag,
)

sleep.set_upstream(send_session_reminders)
