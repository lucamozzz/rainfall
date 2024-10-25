"""
 Copyright (C) 2023 Università degli Studi di Camerino.
 Authors: Alessandro Antinori, Rosario Capparuccia, Riccardo Coltrinari, Flavio Corradini, Marco Piangerelli, Barbara Re, Marco Scarpetta, Luca Mozzoni, Vincenzo Nucci

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as
 published by the Free Software Foundation, either version 3 of the
 License, or (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
 """

from fastapi import APIRouter, Response, Depends
from starlette.status import HTTP_204_NO_CONTENT
import service.folder_service as fs
from schemas.file_schemas import FileConfigSchema
from schemas.auth import User
from controller.standard_auth_api import get_current_user
from fastapi.responses import FileResponse, Response

router = APIRouter()


@router.get('/{folder_name}/{file_name}', response_class=FileResponse)
async def get_file_from_folder(folder_name: str, file_name: str, user: User = Depends(get_current_user)):
    """ Gets the content of a file. """
    file_path = fs.get_file_from_folder(folder_name, file_name, user['username'])
    if file_path is None:
        return Response(status_code=404)
    return FileResponse(file_path, filename=file_name, media_type="text/plain")


@router.post('/file')
async def add_file_to_folder(config: FileConfigSchema, user: User = Depends(get_current_user)):
    """ Saves a file in a folder. """
    fs.add_file_to_folder(config, user['username'])


@router.post('/{folder_name}')
async def create_folder(folder_name: str, user: User = Depends(get_current_user)):
    """ Creates a new folder. """
    fs.create_folder(folder_name, user['username'])
    return Response(content=None, status_code=204)


@router.get('', response_model=list[object])
async def get_folders(user: User = Depends(get_current_user)):
    """ Gets all the folders. """
    return fs.get_folder_names(user['username'])


@router.get('/{folder_name}')
async def get_folder_content(folder_name: str, user: User = Depends(get_current_user)):
    """ Gets info (name, size, created_at) about the files in the folder. """
    return fs.get_folder_content(folder_name, user['username'])


@router.delete('/{folder_name}', status_code=204, response_class=Response)
async def delete_folder(folder_name: str, user: User = Depends(get_current_user)):
    """ Deletes a folder. """
    fs.delete_folder(folder_name, user['username'])
    return Response(content=None, status_code=204)


@router.delete('/{folder_name}/files/{file_name}', status_code=204, response_class=Response)
async def delete_file(folder_name: str, file_name: str, user: User = Depends(get_current_user)) -> None:
    """ Deletes a file in a folder. """
    fs.delete_file(folder_name, file_name, user['username'])
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.get('/share/{folder}/users')
async def get_folder_users(folder: str, user: User = Depends(get_current_user)):
    """ Gets the users that can access the folder. """
    return fs.get_folder_users(folder, user['username'])


@router.post('/share/{folder_name}/{receiver}')
async def share_folder(folder_name: str, receiver: str, user: User = Depends(get_current_user)):
    """ Gives access to a folder to the specified user. """
    fs.share_folder(folder_name, user['username'], receiver)
    return Response(content=None, status_code=204)


@router.post('/unshare/{folder_name}/{receiver}')
async def unshare_folder(folder_name: str, receiver: str, user: User = Depends(get_current_user)):
    """ Removes access to a folder from the specified user. """
    fs.unshare_folder(folder_name, user['username'], receiver)
    return Response(content=None, status_code=204)