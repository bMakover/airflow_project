# Your existing DAG file (e.g., my_dag.py)
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from dash_app import create_dashboard_layout

default_args = {
    'owner': 'batsheva',
    'start_date': datetime(2023, 7, 16),
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    dag_id='docker_dash',
    default_args=default_args,
    start_date=datetime(2023, 5, 26),
    schedule_interval='@daily'
) as dag:

    generate_plot_task = PythonOperator(
        task_id='generate_plot',
        python_callable=create_dashboard_layout,
    )

generate_plot_task
