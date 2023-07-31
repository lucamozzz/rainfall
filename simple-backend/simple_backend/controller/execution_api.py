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

from json import loads
import asyncio
from typing import List, Union
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import Response
from fastapi.requests import Request
from starlette.responses import StreamingResponse
from starlette.status import HTTP_200_OK
from sse_starlette.sse import EventSourceResponse
from simple_backend.schemas.nodes import UINode, CustomNodeStructure, NodeStructure
from simple_backend.service.config_service import get_requirements, generate_script
import simple_backend.service.execution_service as es
from celery.worker.control import revoke
from celery.states import ALL_STATES
from dotenv import load_dotenv
load_dotenv()


MESSAGE_STREAM_DELAY = 1  # second
MESSAGE_STREAM_RETRY_TIMEOUT = 15000  # milisecond

router = APIRouter()

@router.post('', status_code=200, response_class=Response)
def execute(config: dict, background_tasks: BackgroundTasks) -> None:
    """
    Api used to launch the execution of a dataflow
    """
    execution_id = es.create_execution_instance(config)
    background_tasks.add_task(es.execute_dataflow.delay, execution_id)
    # task_id = es.execute_dataflow.delay(execution_id)
    # revoke(ALL_STATES, task_id=task_id, terminate=True)
    return Response(status_code=HTTP_200_OK, background=background_tasks)


@router.post('/requirements', response_model=List[str])
def post_nodes_requirements(libs: List[str], ui_nodes: List[UINode],
                                  ui_structures: dict[str, Union[CustomNodeStructure, NodeStructure]]):
    """
    Api used to retrieve the requirements
    """
    return get_requirements(libs, ui_nodes, ui_structures)
    

@router.get('/statuses')
def get_executions():
    """
    Api used to retrieve the status of all the executions
    """
    return es.get_all_executions_status()
    

@router.get('/{id}/status')
def get_execution_status(id: str):
    """
    Api used to retrieve the status of a specific execution
    """
    return es.get_execution_field(id, 'status')


@router.get('/{id}/info')
def get_execution_logs(id: str):
    """
    Api used to retrieve the info of a specific execution
    """
    return {
        'id': id,
        'status': es.get_execution_field(id, 'status'),
        'logs': es.get_execution_field(id, 'logs'),
        'ui': es.get_execution_field(id, 'ui'),
    }


@router.delete('/{id}/info')
def delete_execution_logs(id: str):
    """
    Api used to retrieve the info of a specific execution
    """
    return es.delete_execution_info(id)


@router.get('/{id}/ui')
def get_execution_logs(id: str):
    """
    Api used to retrieve the ui of a specific execution
    """
    return es.get_execution_field(id, 'ui')


@router.get("/watch")
async def sse_status_updates():
    return EventSourceResponse(content=es.watch_executions())


@router.get("/watch/{id}")
async def sse_logs_updates(id: str):
    if es.is_execution_running(id):
        return EventSourceResponse(content=es.watch_execution(id))
    else:
        return Response(status_code=204)
    # else:
    #     return Response(status_code=HTTP_200_OK, media_type="text/event-stream")
