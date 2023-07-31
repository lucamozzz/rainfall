"""
 Copyright (C) 2023 Università degli Studi di Camerino and Sigma S.p.A.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

import uuid
import os
import json
import subprocess
import requests
import time
from json import loads
from datetime import datetime
from pymongo import MongoClient
from celery import Celery

from virtualenv import cli_run
from simple_backend.errors import BadRequestError
from simple_backend.schemas.nodes import ConfigurationSchema
from simple_backend.service.config_service import generate_script
from dotenv import load_dotenv
load_dotenv()


BROKER_URL = os.environ.get("BROKER_URL")
BROKER_USER = os.environ.get("BROKER_USER")
BROKER_PASSWORD = os.environ.get("BROKER_PASSWORD")
BROKER_MANAGEMENT_URL = os.environ.get("BROKER_MANAGEMENT_URL")
PENDING = "Pending"
RUNNING = "Running"
SUCCESS = "Success"
ERROR = "Error"
EXECUTION_LOGS_QUEUE = 'logs'
DATABASE_NAME='rainfall'
EXECUTIONS_COLLECTION_NAME='executions'
WORKER_EXECUTION_PATH='/tmp/executions'

celery = Celery(__name__)
celery.conf.broker_url = BROKER_URL
celery.conf.result_backend = os.environ.get("DATABASE_URL")


@celery.task(name="execute_dataflow", ignore_result=True)
def execute_dataflow(execution_id: str):
    execution = get_execution_instance(execution_id)
    if execution:
        path = WORKER_EXECUTION_PATH + str(execution_id) + '/'

        if not os.path.isdir(path):
            os.mkdir(path)
        with open(os.path.join(path, "script.py"), "w+") as sp:
            sp.write(execution['script'])
        with open(os.path.join(path, "requirements.txt"), "w+") as req:
            req.write(execution['requirements'])
        with open(os.path.join(path, "ui.json"), "w+") as ui:
            ui.write(execution['ui'])

        venv_loc = os.path.join(path, "venv")
        cli_run([venv_loc])

        if str(os.name).lower() == "nt":
            venv_scripts_loc = "Scripts"
        elif str(os.name).lower() == "posix":
            venv_scripts_loc = "bin"
        else:
            raise BadRequestError("unsupported OS")

        os.chdir(path)
        pip_loc = os.path.join(venv_loc, venv_scripts_loc, 'pip')
        os.system(pip_loc + " install --upgrade pip")
        os.system(pip_loc + " install -r requirements.txt")

        set_execution_field(execution_id, 'status', RUNNING)

        cmd = [os.path.join(venv_loc, venv_scripts_loc, "python"), "script.py"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=path, universal_newlines=True, bufsize=1, text=True)

        try:
            client = MongoClient(os.environ.get("DATABASE_URL"))
            db = client[DATABASE_NAME]
            collection = db[EXECUTIONS_COLLECTION_NAME]
            execution = collection.find_one({"_id": execution_id})

            while True:
                line = process.stdout.readline()
                if line == '' and process.poll() is not None:
                    break
                status = line.strip().split('|')[1]
                collection.update_one({"_id": execution_id}, {"$push": {"logs": line.strip()}})

            if status == 'SUCCESS':
                set_execution_field(execution_id, 'status', SUCCESS)
            else:
                set_execution_field(execution_id, 'status', ERROR)
            
        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            process.wait()
            client.close()


def create_execution_instance(config):
    execution_id = str(uuid.uuid4()) 
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config: ConfigurationSchema = ConfigurationSchema.parse_obj(loads(config['config']))
    script = generate_script(config.nodes)

    execution = {
        "_id": execution_id,
        "created_at": current_time,
        "status": PENDING,
        "logs": list(),
        "script": script,
        "requirements": "\n".join(config.dependencies),
        "ui": config.ui.json(separators=(',', ':'))
    }

    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        collection.insert_one(execution)
        print("Dataflow execution succesfully queued.")
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()
        return execution_id


def get_execution_instance(execution_id: str):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        execution = collection.find_one({"_id": execution_id})
        if execution:
            return execution
        
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def is_execution_running(id: str):
    status: str = get_execution_field(id, 'status')
    if status == 'Success' or status == 'Error':
        return False
    else:
        return True


def get_all_executions_status():
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        
        projection = {"_id": 1, "status": 1}
        documents = list(collection.find({}, projection))

        return [{"id": str(doc["_id"]), "status": doc["status"]} for doc in documents]


    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def get_execution_field(execution_id, field_name):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        execution = collection.find_one({"_id": execution_id}, {field_name: 1})

        if execution:
            return execution.get(field_name)

    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def set_execution_field(execution_id, field_name, field_value):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        execution = collection.find_one({"_id": execution_id})

        if execution:
            # Update the field with the new value
            collection.update_one({"_id": execution_id}, {"$set": {field_name: field_value}})
            print(f"Document with ID {execution_id} updated successfully.")
        
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def delete_execution_info(execution_id):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        collection.delete_one({"_id": execution_id})
        
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def watch_executions():
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]

        pipeline = [{'$match': {'operationType': 'update'}}]
        with collection.watch(pipeline) as stream:
            for change in stream:
                updated_id = str(change["documentKey"]["_id"])
                updated_status = change["updateDescription"]["updatedFields"].get('status')
                if updated_status is not None:
                    data = {"id": updated_id, "status": updated_status}
                    event_data = f"{json.dumps(data)}"
                    yield event_data
    
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def watch_execution(id: str):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[EXECUTIONS_COLLECTION_NAME]
        pipeline = [{'$match': {'operationType': 'update'}}]
        with collection.watch(pipeline) as stream:
            for change in stream:
                execution_update = change["updateDescription"]["updatedFields"]
                if 'status' in execution_update:
                    if execution_update['status'] != 'Running':
                        data = {"id": id, "status": execution_update['status']}
                        event_data = f"data: {json.dumps(data)}\n"
                        return event_data
                else:
                    logs_values = [value for key, value in execution_update.items() if "logs" in key]
                    data = {"id": id, "logs": logs_values[0]}
                    event_data = f"{json.dumps(data)}"
                    yield event_data

    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()
