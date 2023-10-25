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
import subprocess
from json import loads, dumps
from datetime import datetime
import randomname
from celery import Celery
from celery.contrib.abortable import AbortableTask
from virtualenv import cli_run
import shutil
from simple_backend.errors import BadRequestError
from simple_backend.schemas.nodes import ConfigurationSchema
from simple_backend.service.database_service import get_database
from simple_backend.service.config_service import generate_script
from dotenv import load_dotenv
load_dotenv()


PENDING = "Pending"
RUNNING = "Running"
SUCCESS = "Success"
ERROR = "Error"
REVOKED = "Revoked"
DATABASE_NAME='rainfall'
EXECUTIONS_COLLECTION_ID='executions'
WORKER_EXECUTION_PATH='/tmp/executions'

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("BROKER_URL")
celery.conf.result_backend = os.environ.get("MONGODB_URL")
db = get_database()


@celery.task(name="execute_dataflow", ignore_result=True, bind=True, base=AbortableTask)
def execute_dataflow(self, execution_id: str):
    def cleanup(path: str):
        if os.path.isdir(path):
            shutil.rmtree(path)

    execution = get_execution_instance(execution_id)
    if execution:
        set_execution_field(execution_id, 'status', RUNNING)
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
        
        if self.is_aborted():
            cleanup(path)
            return 'Task aborted'

        os.chdir(path)
        pip_loc = os.path.join(venv_loc, venv_scripts_loc, 'pip')
        os.system(pip_loc + " install --upgrade pip")
        os.system(pip_loc + " install -r requirements.txt")

        if self.is_aborted():
            cleanup(path)
            return 'Task aborted'

        cmd = [os.path.join(venv_loc, venv_scripts_loc, "python"), "script.py"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, cwd=path, universal_newlines=True, bufsize=1, text=True)

        while True:
            if self.is_aborted():
                cleanup(path)
                return 'Task aborted'
            line = process.stdout.readline()
            if line == '' and process.poll() is not None:
                break
            status = line.strip().split('|')[1]
            update_execution_field(execution_id, 'logs', line.strip())

        if status == 'SUCCESS':
            set_execution_field(execution_id, 'status', SUCCESS)
        else:
            set_execution_field(execution_id, 'status', ERROR)

        cleanup(path)
        process.wait()


def revoke_execution(execution_id: str):
    task_id = get_execution_field(execution_id, 'celery_task_id')
    task = execute_dataflow.AsyncResult(task_id)
    task.abort()
    set_execution_field(execution_id, 'status', REVOKED)


def create_execution_instance(config):
    execution_id = str(uuid.uuid4())
    execution_name = randomname.generate()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    config: ConfigurationSchema = ConfigurationSchema.parse_obj(loads(config['config']))
    script = generate_script(config.nodes)
    execution = {
        "_id": execution_id,
        "celery_task_id": None,
        "name": execution_name,
        "status": PENDING,
        "logs": list(),
        "script": script,
        "requirements": "\n".join(config.dependencies),
        "ui": config.ui.json(separators=(',', ':')),
        "created_at": current_time,
    }
    db.create_document(EXECUTIONS_COLLECTION_ID, execution)
    return execution_id


def get_execution_instance(execution_id: str):
    return db.get_document(EXECUTIONS_COLLECTION_ID, {"_id": execution_id})


def delete_execution_instance(execution_id: str):
    return db.delete_document(EXECUTIONS_COLLECTION_ID, execution_id)


def get_execution_field(execution_id: str, field_name: str):
    return db.get_document_field(EXECUTIONS_COLLECTION_ID, execution_id, field_name)


def set_execution_field(execution_id: str, field_name: str, field_value: str):
    db.set_document_field(EXECUTIONS_COLLECTION_ID, execution_id, field_name, field_value)


def update_execution_field(execution_id: str, field_name: str, field_value: str):
    db.push_document_array_field(EXECUTIONS_COLLECTION_ID, execution_id, field_name, field_value)


def get_all_executions_status():
    return db.get_all_documents_fields(EXECUTIONS_COLLECTION_ID, {"_id": 1, "status": 1, "name": 1})


def watch_executions():
    return db.watch_executions()


def watch_executions(execution_id: str):
    return db.watch_execution(execution_id)


# TODO: fix this
# def watch_execution(execution_id: str):
#     def update_function(item_update):
#         if 'status' in item_update:
#             if item_update['status'] != 'Running':
#                 data = {"id": execution_id, "status": item_update['status']}
#                 event_data = f"data: {dumps(data)}\n"
#                 return event_data
#         else:
#             logs_values = [value for key, value in item_update.items() if "logs" in key]
#             data = {"id": execution_id, "logs": logs_values[0]}
#             event_data = f"{dumps(data)}"
#             yield event_data

#     yield db.watch_item(EXECUTIONS_COLLECTION_ID, update_function)


# TODO: fix this
# def watch_executions():
#     def update_function(item_update, pipeline_id):
#         updated_status = item_update.get('status')
#         if updated_status is not None:
#             data = {"id": pipeline_id, "status": updated_status}
#             event_data = f"{dumps(data)}"
#             yield event_data

#     yield db.watch_items(EXECUTIONS_COLLECTION_ID, update_function)
