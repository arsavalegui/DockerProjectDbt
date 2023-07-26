import airflow.utils.dates
import pandas as pd

from airflow.models import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from airflow.operators.python_operator import PythonOperator
from datetime import datetime

from sqlalchemy import create_engine, inspect, Column, Integer, String, DateTime, text, Float, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Define la función que leerá el archivo .csv y cargará los datos en PostgreSQL
def load_csv_to_postgres():
    # Lee el archivo .csv y crea un DataFrame de Pandas
    dat = pd.read_csv('/opt/airflow/dags/data2.csv', sep=',')

    engine = create_engine('postgresql://airflow:airflow@host.docker.internal:5434/airflow')

    existing_tables = engine.table_names()
    if "dron_table" in existing_tables:
        return

    Base = declarative_base()
    class Table(Base):
        __tablename__ = 'dron_table'

        track_id  = Column(Integer, primary_key=True)
        type = Column(String)
        traveled_d  = Column(Float)
        avg_speed = Column(Float)
        lat = Column(Float)
        lon = Column(Float)
        speed = Column(Float)
        lon_acc = Column(Float)
        lat_acc = Column(Float)
        time = Column(Float)

    conexion = engine.connect()
    Session = sessionmaker(bind=engine)
    sesion = Session()
    Base.metadata.create_all(engine)
    Table_dron = [Table(track_id=dat['track_id'], type=dat[' type'], traveled_d=dat[' traveled_d'], avg_speed=dat[' avg_speed'], lat=dat[' lat'], lon=dat[' lon'], speed=dat[' speed'], lon_acc=dat[' lon_acc'], lat_acc=dat[' lat_acc'], time=dat[' time']) for index, dat in dat.iterrows()]

    sesion.add_all(Table_dron)
    sesion.commit()
    sesion.close()

args = {
    'owner': 'airflow',
    'email_on_failure': False,
	'email': ['200300600@ucaribe.edu.mx']
}

dag = DAG(
   dag_id="ELT",
   default_args=args,
   schedule_interval=None,
   start_date=airflow.utils.dates.days_ago(1),
   catchup=False,
 
)

create_extract_data = PythonOperator(
    task_id="create_extract_data",
    python_callable=load_csv_to_postgres,
    dag=dag,
)

dbt_run = BashOperator(
    task_id='object_transformation.sql',
    bash_command='cd /opt/airflow/demo && dbt run', 
    
    dag=dag 
)

create_extract_data>> dbt_run

if __name__ == "__main__":
    dag.cli()