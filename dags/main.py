from airflow import DAG
import pendulum
from datetime import datetime, timedelta
from api.video_stats import get_playlist_id,get_video_id, extract_video_data, save_to_json
from datawarehouse.dwh import staging_table, core_table

local_tz=pendulum.timezone("Europe/Paris")

default_args = {
    "owner": "dataeng",
    "depends_on_past": False,
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),
    #"end_date": None,
    "email": ["email@engineer.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "max_acrive_runs": 1,
    "dagrun_timeout": timedelta(hours=1)
   # "retries": 1,
   # "retry_delay": timedelta(minutes=5),
   # "retry_exponential_backoff": False,
   # "max_retry_delay": None,
   # "execution_timeout": None,
   # "on_failure_callback": None,
   # "on_success_callback": None,
   # "on_retry_callback": None,
   # "sla": None,
   # "sla_miss_callback": None,
   # "schedule_interval": None,  # moved to DAG() in newer versions
}

with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='DAG to produce json file with the raw data',
    schedule='0 14 * * *',
    catchup=False
) as dag:
    #defin tasks
    playlist_id=get_playlist_id()
    video_ids=get_video_id(playlist_id)
    extract_data=extract_video_data(video_ids)
    save_to_json_task=save_to_json(extract_data)

    #define dependencies
    playlist_id>>video_ids>>extract_data>>save_to_json_task

# DAG 2: update_db
with DAG(
    dag_id="update_db",
    default_args=default_args,
    description="DAG to process JSON file and insert data into both staging and core schemas",
    catchup=False,
    schedule='0 14 * * *',
) as dag_update:

    # Define tasks
    update_staging = staging_table()
    update_core = core_table()

    # Define dependencies
    update_staging >> update_core



