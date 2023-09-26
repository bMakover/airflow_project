from datetime import datetime
from airflow import DAG
import pandas as pd
from datetime import datetime, timedelta
import psycopg2
from airflow.operators.python_operator import PythonOperator
import os
default_args = {
    'owner': 'batsheva',
    'retries': 5,
    'retry_delay': timedelta(minutes=2)
}




def clean_data(ti, **kwargs):

    csv_files = [filename for filename in os.listdir('/app/data/') if filename.endswith('.csv') and filename != 'wine.csv']


    cleaned_data = pd.DataFrame()

    for csv_file in csv_files:
        csv_path = f'/app/data/{csv_file}'
        data = pd.read_csv(csv_path)
        # Replace null values with 'Unknown'
        data['country'].fillna('Unknown', inplace=True)

        # Fill null values in numeric columns with the mean
        data['points'].fillna(data['points'].mean(), inplace=True)
        data['price'].fillna(data['price'].mean(), inplace=True)

        data['designation'].fillna(data['designation'].mode()[0], inplace=True)

        str_col = ['country', 'designation', 'description', 'province', 'region_1', 'region_2', 'taster_name', 'taster_twitter_handle', 'title', 'winery', 'variety']
        for col in str_col:
            data[col] = data[col].fillna('').astype(str).str.slice(0, 500)

        
        cleaned_data = cleaned_data.append(data, ignore_index=True)

        
        os.remove(csv_path)

    ti.xcom_push(key='data', value=cleaned_data)
    return cleaned_data

def store_data(ti, **kwargs):
    data = ti.xcom_pull(task_ids='clean_data', key='data')
    conn = psycopg2.connect( database="postgres", user="postgres", password="postgres", host="db", port="5432")
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Wines(

        id SERIAL PRIMARY KEY,
        country VARCHAR(500),
        description VARCHAR(500),
        designation VARCHAR(500),
        points INT,
        price INT,
        province VARCHAR(500),
        region_1 VARCHAR(500),
        region_2 VARCHAR(500),
        taster_name VARCHAR(500),
        taster_twitter_handle VARCHAR(500),
        title VARCHAR(500),
        variety VARCHAR(500),
        winery VARCHAR(500)
            );
    
    """
    )
    for _, row in data.iterrows():
        sql = f"""INSERT INTO Wines (

        country,
        description,
        designation,
        points, 
        price,
        province,
        region_1,
        region_2,
        taster_name,
        taster_twitter_handle,
        title,
        variety,
        winery ) VALUES (%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s, %s,%s)"""
        values = (row['country'],row['description'],row['designation'], row['points'],row['price'],row['province'],row['region_1'],row['region_2'],row['taster_name'],row['taster_twitter_handle'],row['title'],row['variety'],row['winery'])
        cur.execute(sql, values)



    conn.commit()
    cur.close()
    conn.close()  

with DAG(
    dag_id='docker_consumer',
    default_args=default_args,
    description='consumer',
    start_date=datetime(2023, 7, 15, 2),
    schedule_interval='*/5 * * * *'
) as dag:
    task1 = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data,
        provide_context=True
    )

    task2 = PythonOperator(
        task_id='store_data',
        python_callable=store_data,
        provide_context=True
    )

    task1 >> task2  
