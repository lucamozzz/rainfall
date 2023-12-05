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

import uuid
from typing import List
from datetime import datetime
from simple_backend.service.database_service import get_database
from simple_backend.schemas.nodes import FileConfigSchema
from datetime import datetime

DATABASE_NAME='rainfall'
FOLDERS_COLLECTION_NAME='folders'
FILES_COLLECTION_NAME='files'
USERS_COLLECTION_NAME='users'
db = get_database()


def get_folder_names(user) -> List[str]:
    """ Returns info about the folders. """
    target_id = user["email"]
    organization = user["organization"]
    query = {
        "$or": [
            {"users": target_id},
            {"users": organization}
        ]
    }
    repos = db.get_all_documents_fields(FOLDERS_COLLECTION_NAME, {"_id": 1, "name": 1, "files": 1, "owner": 1}, query)
    for repo in repos:
        if repo["owner"] == target_id:
            repo["owner"] = True
        else: 
            repo["owner"] = False
    return repos


def get_file_from_folder(file_id: str):
    """ Returns the content of a file in a folder."""
    return db.get_document(FILES_COLLECTION_NAME, {"_id": file_id}, {"name": 1, "content": 1})


def create_folder(repository_name: str, user) -> None:
    """ Creates a new folder. """
    repository_id = str(uuid.uuid4())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    repo_users = list()
    repo_users.append(user["email"])
    repository = {
        "_id": repository_id,
        "name": repository_name,
        "created_at": current_time,
        "files": list(),
        "owner": user["email"],
        "organization": user["organization"],
        "users": repo_users
    }
    db.create_document(FOLDERS_COLLECTION_NAME, repository)


# TODO: check if repo is the owner of the folder
def share_folder(folder_id: str, receiver_id: str):
    """ Shares a folder with a user. """
    users: dict = db.get_all_documents_fields(USERS_COLLECTION_NAME, {"_id": 1, "organization": 1})
    receiver_exists = False
    for user in users:
        if receiver_id == user["id"] or receiver_id == user["organization"]:
            receiver_exists = True
    
    folder_users = db.get_document_field(FOLDERS_COLLECTION_NAME, folder_id, "users")
    if receiver_exists and receiver_id not in folder_users:
        db.push_document_array_field(FOLDERS_COLLECTION_NAME, folder_id, "users", receiver_id)


# TODO: check if repo is owner, check if receiver exists
def unshare_folder(folder_id: str, receiver_id: str):
    """ Unshares a folder with a user. """
    db.pull_document_array_field(FOLDERS_COLLECTION_NAME, folder_id, "users", receiver_id)


def get_folder_users(folder_id: str):
    """ Returns the users of a folder. """
    return db.get_document_field(FOLDERS_COLLECTION_NAME, folder_id, "users")


def delete_folder(folder_id: str) -> None:
    """ Shares a folder with a user. """
    db.delete_document(FOLDERS_COLLECTION_NAME, folder_id)


def get_folder_content(folder_id: str) -> List[list]:
    """ Returns info about the content of a folder. """
    return db.get_all_documents_fields(FILES_COLLECTION_NAME, {"_id": 1, "name": 1, "created_at": 1}, {"folder": folder_id})


def add_file_to_folder(config: FileConfigSchema) -> str:
    """ Stores a file in folder. """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    file_id = 'file-' + str(uuid.uuid4())
    file = {
        "_id": file_id,
        "created_at": current_time,
        "name": config.name,
        "content": config.content,
        "folder": config.folder
    }
    db.create_document(FILES_COLLECTION_NAME, file)
    db.push_document_array_field(FOLDERS_COLLECTION_NAME, config.folder, "files", file_id)


def delete_file(folder_id: str, file_id: str) -> str:
    """ Deletes a file from a folder. """
    folder = db.get_document(FOLDERS_COLLECTION_NAME, {"_id": folder_id})
    if folder:
        db.pull_document_array_field(FOLDERS_COLLECTION_NAME, folder_id, "files", file_id)
        db.delete_document(FILES_COLLECTION_NAME, file_id)
    return file_id
