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

from fastapi import APIRouter, Response
from starlette.status import HTTP_204_NO_CONTENT
from simple_backend import config
from simple_backend.errors import BadRequestError
from simple_backend.schemas.dataflow import DataFlow
from simple_backend.schemas.repository_schemas import RepositoryGet, RepositoryPost
from simple_backend.service import repository_service as rs


router = APIRouter()


@router.get('', response_model=list[object])
async def get_repositories():
    """ Gets all the repositories. """
    return rs.get_repositories_names()


@router.get('/archived', response_model=list[object])
async def get_archived_repositories():
    """ Gets all the archived repositories. """
    return rs.get_archived_repositories_names()


@router.get('/{repository}')
async def get_repository(repository: str):
    """ Gets the content of the repository. """
    return rs.get_repository_content(repository)


@router.post('/{repository_name}')
async def create_repository(repository_name: str):
    """ Creates a new repository. """
    rs.create_repository(repository_name)

    return Response(content=None, status_code=204)


@router.delete('/{repository}', status_code=204, response_class=Response)
async def delete_repository(repository: str):
    """ Delete a repository. """
    rs.delete_repository(repository)

    return Response(content=None, status_code=204)


@router.post('/archived/{repository}', responses={200: {"model": RepositoryPost}, 404: {"schema": BadRequestError}})
async def toggle_repository_archiviation(repository: str):
    """ Archive/unarchive a repository. """
    return rs.toggle_repository_archiviation(repository)


@router.get('/{repository}/dataflows/{id}')
async def get_dataflow(repository: str, id: str):
    """ Gets the specified Dataflow from the repository. """
    return rs.get_dataflow_from_repository(repository, id)
    

@router.get('/{repository}/dataflows/{id}/{field}')
def get_execution_status(id: str, field: str):
    """
    Api used to retrieve a field of a specific execution
    """
    return rs.get_dataflow_field(id, field)


@router.delete('/{repository}/dataflows/{id}', status_code=204, response_class=Response)
async def delete_dataflow(repository: str, id: str) -> None:
    """ Deletes a Dataflow in the repository. """
    rs.delete_dataflow(repository, id)
    return Response(status_code=HTTP_204_NO_CONTENT)
