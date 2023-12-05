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

import sys
import uuid
import os
from typing import List
from pymongo import MongoClient
from datetime import datetime
from simple_backend import config
from simple_backend.errors import BadRequestError
from simple_backend.service.database_service import get_database

DATABASE_NAME='rainfall'
REPOSITORIES_COLLECTION_NAME='repositories'
DATAFLOWS_COLLECTION_NAME='dataflows'
USERS_COLLECTION_NAME='users'
db = get_database()


def get_repositories_names(user) -> List[str]:
    """ Returns the immediate subdirectories names of the output dir. """
    target_id = user["email"]
    organization = user["organization"]
    query = {
        "archived": False,
        "$or": [
            {"users": target_id},
            {"users": organization}
        ]
        }
    repos = db.get_all_documents_fields(REPOSITORIES_COLLECTION_NAME, {"_id": 1, "name": 1, "owner": 1}, query)
    for repo in repos:
        if repo["owner"] == target_id:
            repo["owner"] = True
        else: 
            repo["owner"] = False
    return repos


def get_archived_repositories_names(user) -> List[str]:
    """ Returns the immediate subdirectories names of the output dir. """
    target_id = user["email"]
    return db.get_all_documents_fields(REPOSITORIES_COLLECTION_NAME, {"_id": 1, "name": 1}, {"archived": True, "users": {"$in": [target_id]}})


def create_repository(repository_name: str, user) -> None:
    repository_id = str(uuid.uuid4())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    repo_users = list()
    repo_users.append(user["email"])
    repository = {
        "_id": repository_id,
        "name": repository_name,
        "created_at": current_time,
        "dataflows": list(),
        "archived": False,
        "owner": user["email"],
        "organization": user["organization"],
        "users": repo_users
    }
    db.create_document(REPOSITORIES_COLLECTION_NAME, repository)


# TODO: check if repo owner, check if receiver exists
def share_repository(repository_id: str, receiver_id: str):
    users: dict = db.get_all_documents_fields(USERS_COLLECTION_NAME, {"_id": 1, "organization": 1})
    receiver_exists = False
    for user in users:
        if receiver_id == user["id"] or receiver_id == user["organization"]:
            receiver_exists = True
    
    repo_users = db.get_document_field(REPOSITORIES_COLLECTION_NAME, repository_id, "users")
    if receiver_exists and receiver_id not in repo_users:
        db.push_document_array_field(REPOSITORIES_COLLECTION_NAME, repository_id, "users", receiver_id)


# TODO: check if repo owner, check if receiver exists
def unshare_repository(repository_id: str, receiver_id: str):
    db.pull_document_array_field(REPOSITORIES_COLLECTION_NAME, repository_id, "users", receiver_id)


def get_repository_users(repository_id: str):
    return db.get_document_field(REPOSITORIES_COLLECTION_NAME, repository_id, "users")


def delete_repository(repository_id: str) -> None:
    db.delete_document(REPOSITORIES_COLLECTION_NAME, repository_id)


def toggle_repository_archiviation(repository_id):
    flag = db.get_document_field(REPOSITORIES_COLLECTION_NAME, repository_id, "archived")
    db.set_document_field(REPOSITORIES_COLLECTION_NAME, repository_id, "archived", not flag)


def get_repository_content(repository_id: str) -> List[list]:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    return db.get_document_field(REPOSITORIES_COLLECTION_NAME, repository_id, "dataflows")


def get_dataflow_from_repository(repository_id: str, dataflow_id: str):
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    repository = db.get_document(REPOSITORIES_COLLECTION_NAME, {"_id": repository_id}, {"dataflows": 1})
    if repository:
        return db.get_document(DATAFLOWS_COLLECTION_NAME, {"_id": dataflow_id})
    else:
        return []


def add_dataflow_to_repo(dataflow, repository_name) -> str:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    repository = db.get_document(REPOSITORIES_COLLECTION_NAME, {"name": repository_name})
    if repository:
        db.create_document(DATAFLOWS_COLLECTION_NAME, dataflow)
        db.push_document_array_field(REPOSITORIES_COLLECTION_NAME, repository['_id'], "dataflows", dataflow["_id"])


def delete_dataflow(repository_id: str, dataflow_id: str) -> str:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    repository = db.get_document(REPOSITORIES_COLLECTION_NAME, {"_id": repository_id})
    if repository:
        db.pull_document_array_field(REPOSITORIES_COLLECTION_NAME, repository_id, "dataflows", dataflow_id)
        db.delete_document(DATAFLOWS_COLLECTION_NAME, dataflow_id)
    return dataflow_id


def get_dataflow_field(dataflow_id, field_name):
    return db.get_document_field(DATAFLOWS_COLLECTION_NAME, dataflow_id, field_name)
