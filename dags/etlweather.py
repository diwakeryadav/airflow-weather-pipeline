from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.decorators import task
import pendulum
from pendulum import datetime
import requests

LATITUDE = '51.5074'
LONGITUDE = '-0.1278'
POSTGRES_CONN_ID = 'postgres_default'
API_CONN_ID = 'open_meteo_api'

default_args = {
    'owner':'airflow'
}

## DAG 
with DAG(dag_id='weather_etl_pipeline', 
         default_args = default_args,
         start_date = pendulum.now().subtract(days=1),
         schedule = '@daily',
         catchup = False) as dags:
    
    @task()
    def extract_weather_data():
        '''Extract weather data from Open-Meteo API using Airflow Connection'''
        # To interact with the API we need the HTTP Hook to get the weather data 
        # Use HTTP hook to get connection details from AIRFLOW connection
        # Build the API endpoint
         
        endpoint =f'/v1/forecast?latitude={LATITUDE}&longitude={LONGITUDE}&current_weather=True'

        # make request via the HTTP hook
    
        response=requests.get(f'https://api.open-meteo.com{endpoint}')
        if response.status_code==200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch weather data : {response.status_code}")
        
    @task()
    def transform_weather_data(weather_data):
        """Transform the extracted weather data"""
        current_weather = weather_data['current_weather']
        transformed_data ={
            'latitude' : LATITUDE,
            'longitude' : LONGITUDE,
            'temperature' : current_weather['temperature'],
            'windspeed' : current_weather['windspeed'],
            'winddirection' : current_weather['winddirection'],
            'weathercode' : current_weather['weathercode'] 
        }
        return transformed_data
    
    @task()
    def load_weather_data(transformed_data):
        pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()

        cursor.execute("DROP TABLE IF EXISTS weather_data;")
    
        cursor.execute("""
        CREATE TABLE weather_data(
            latitude FLOAT,
            longitude FLOAT,
            temperature FLOAT,
            windspeed FLOAT,
            winddirection FLOAT,
            weathercode INT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
            """)

        cursor.execute("""
        INSERT INTO weather_data(latitude, longitude, temperature, windspeed, winddirection, weathercode)
        VALUES (%s,%s,%s,%s,%s,%s)""",(
            transformed_data['latitude'],
            transformed_data['longitude'],
            transformed_data['temperature'],
            transformed_data['windspeed'],
            transformed_data['winddirection'],
            transformed_data['weathercode']
        ))

        conn.commit()
        cursor.close()

    # DAG workflow - ETL pipeline
    weather_data = extract_weather_data()
    transformed_data=transform_weather_data(weather_data)
    load_weather_data(transformed_data)