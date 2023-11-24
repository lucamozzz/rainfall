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

from fastapi import APIRouter, Response, Depends
from starlette.status import HTTP_204_NO_CONTENT
import simple_backend.service.folder_service as fs
from simple_backend.schemas.nodes import FileConfigSchema
from simple_backend.controller.standard_auth_api import get_current_user


router = APIRouter()


@router.get('/files/{id}')
async def get_file_from_folder(id: str):
    """ Get the content of a file."""
    return fs.get_file_from_folder(id)


@router.post('/file')
async def add_file_to_folder(config: FileConfigSchema):
    """ Save a file in a folder."""
    fs.add_file_to_folder(config)


@router.post('/{folder_name}')
async def create_repository(folder_name: str, user = Depends(get_current_user)):
    """ Creates a new folder. """
    fs.create_folder(folder_name, user)
    return Response(content=None, status_code=204)


@router.get('', response_model=list[object])
async def get_folders(user = Depends(get_current_user)):
    """ Gets all the folders. """
    return fs.get_folder_names(user)


@router.get('/{folder_id}')
async def get_folder_content(folder_id: str):
    """ Gets the content of the folder. """
    return fs.get_folder_content(folder_id)


@router.get('/{folder}/users')
async def get_folder_users(folder: str):
    """ Gets the users of the folder. """
    return fs.get_folder_users(folder)


@router.post('/{folder_id}/share/{receiver_id}')
async def share_folder(folder_id: str, receiver_id: str):
    """ Shares a folder with the specified user. """
    fs.share_folder(folder_id, receiver_id)
    return Response(content=None, status_code=204)


@router.post('/{folder_id}/unshare/{receiver_id}')
async def unshare_folder(folder_id: str, receiver_id: str):
    """ Unshares a folder with the specified user. """
    fs.unshare_folder(folder_id, receiver_id)
    return Response(content=None, status_code=204)


@router.delete('/{folder_id}', status_code=204, response_class=Response)
async def delete_folder(folder_id: str):
    """ Delete a folder. """
    fs.delete_folder(folder_id)
    return Response(content=None, status_code=204)


@router.delete('/{folder_id}/files/{file_id}', status_code=204, response_class=Response)
async def delete_file(folder_id: str, file_id: str) -> None:
    """ Deletes the specified file in the folder. """
    fs.delete_file(folder_id, file_id)
    return Response(status_code=HTTP_204_NO_CONTENT)
