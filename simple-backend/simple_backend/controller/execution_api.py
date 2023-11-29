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
from typing import List, Union
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from fastapi.requests import Request
from starlette.status import HTTP_200_OK
from sse_starlette.sse import EventSourceResponse
from simple_backend.schemas.nodes import UINode, CustomNodeStructure, NodeStructure
from simple_backend.service.config_service import get_requirements
import simple_backend.service.execution_service as es
from simple_backend.controller.standard_auth_api import get_current_user
from dotenv import load_dotenv
load_dotenv()


MESSAGE_STREAM_DELAY = 1
MESSAGE_STREAM_RETRY_TIMEOUT = 15000

router = APIRouter()

@router.post('', status_code=200, response_class=Response)
def execute(config: dict, user = Depends(get_current_user)) -> None:
    """
    Api used to launch the execution of a dataflow
    """
    execution_id = es.create_execution_instance(config, user)
    task_id = es.execute_dataflow.delay(execution_id)
    es.set_execution_field(execution_id, 'celery_task_id', str(task_id))
    return Response(status_code=HTTP_200_OK)


@router.post('/{id}/revoke')
def revoke_execution(id: str):
    """
    Api used to revoke the execution of a dataflow
    """
    es.revoke_execution(id)
    return Response(status_code=HTTP_200_OK)


@router.post('/requirements', response_model=List[str])
def post_nodes_requirements(libs: List[str], ui_nodes: List[UINode],
                                  ui_structures: dict[str, Union[CustomNodeStructure, NodeStructure]]):
    """
    Api used to retrieve the execution requirements
    """
    return get_requirements(libs, ui_nodes, ui_structures)
    

@router.get('/info')
def get_executions(user = Depends(get_current_user)):
    """
    Api used to retrieve name and status of all the executions
    """
    return es.get_all_executions_status(user)
    

@router.get('/{id}/info/{field}')
def get_execution_status(id: str, field: str):
    """
    Api used to retrieve a field of a specific execution
    """
    return es.get_execution_field(id, field)


@router.get('/{id}/info')
def get_execution_logs(id: str):
    """
    Api used to retrieve the info of a specific execution
    """
    execution = es.get_execution_instance(id)
    return {
        'id': id,
        'status': execution['status'],
        'name': execution['name'],
        'logs': execution['logs'],
        'ui': execution['ui'],
    }


@router.delete('/{id}/info')
def delete_execution_logs(id: str):
    """
    Api used to retrieve the info of a specific execution
    """
    return es.delete_execution_instance(id)


@router.get("/watch")
async def watch_executions():
    """
    Api used to receive updates on the executions
    """
    return EventSourceResponse(content=es.watch_executions())


@router.get("/watch/{id}")
async def watch_execution(id: str):
    """
    Api used to receive updates on a specific execution
    """
    return EventSourceResponse(content=es.watch_execution(id))
