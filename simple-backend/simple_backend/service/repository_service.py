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

import sys
import uuid
import os
from typing import List
from pymongo import MongoClient
from datetime import datetime
from simple_backend import config
from simple_backend.errors import BadRequestError

DATABASE_NAME='rainfall'
REPOSITORIES_COLLECTION_NAME='repositories'
DATAFLOWS_COLLECTION_NAME='dataflows'


try:
    config.BASE_OUTPUT_DIR.mkdir(exist_ok=True)
    config.BASE_OUTPUT_DIR.joinpath('.gitkeep').touch(exist_ok=True)
    config.ARCHIVE_DIR.mkdir(exist_ok=True)
except:
    print('Can\'t create repositories directory!')
    sys.exit(1)

def get_repositories_names() -> List[str]:
    """ Returns the immediate subdirectories names of the output dir. """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        
        filter = {"archived": False}
        projection = {"_id": 1, "name": 1}
        documents = list(collection.find(filter, projection))
        repositories = [{"id": str(doc["_id"]), "name": doc["name"]} for doc in documents]
        return repositories
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def get_archived_repositories_names() -> List[str]:
    """ Returns the immediate subdirectories names of the output dir. """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        
        filter = {"archived": True}
        projection = {"_id": 1, "name": 1}
        documents = list(collection.find(filter, projection))
        repositories = [{"id": str(doc["_id"]), "name": doc["name"]} for doc in documents]
        return repositories
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def create_repository(repository_name: str) -> None:
    repository_id = str(uuid.uuid4())
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    repository = {
        "_id": repository_id,
        "name": repository_name,
        "created_at": current_time,
        "dataflows": list(),
        "archived": False,
    }

    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]

        existing_repository = collection.find_one({"name": repository_name})
        if existing_repository is None:
            collection.insert_one(repository)
        return repository_id
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def delete_repository(repository_id: str) -> None:
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        repository = collection.find_one({"_id": repository_id})
        if repository:
            for df in repository["dataflows"]:
                delete_dataflow(repository_id, df)
            collection.delete_one({"_id": repository_id})
        return repository_id
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def toggle_repository_archiviation(repository_id):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        repository = collection.find_one({"_id": repository_id})

        if repository:
            flag = not repository["archived"]
            print('repo set to: ' + str(flag))
            collection.update_one({"_id": repository_id}, {"$set": {"archived": flag}})
        else: 
            raise BadRequestError(f"Repository does not exists!")
        
        return repository_id
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def archive_repository(repository_id):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        execution = collection.find_one({"_id": repository_id})

        if execution:
            collection.update_one({"_id": repository_id}, {"$set": {"archived": True}})
        else: 
            raise BadRequestError(f"Repository does not exists!")
        
    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def get_repository_content(repository_id: str) -> List[list]:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        # Query the collection to retrieve the specific document
        filter = {"_id": repository_id}
        projection = {"dataflows": 1}
        document = collection.find_one(filter, projection)

        if document:
            dataflows = document.get("dataflows", [])
            return dataflows
        else:
            print("Document not found.")
            return []

    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def get_dataflow_from_repository(repository_id: str, dataflow_id: str):
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        filter = {"_id": repository_id}
        projection = {"dataflows": 1}
        repository = collection.find_one(filter, projection)

        if repository:
            collection = db[DATAFLOWS_COLLECTION_NAME]
            dataflow = collection.find_one({"_id": dataflow_id})
            print(dataflow)
            return dataflow
        else:
            print("Document not found.")
            return []

    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def add_dataflow_to_repo(dataflow, repository) -> str:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        repository = collection.find_one({"name": repository})
        if repository:
            collection.update_one({"_id": repository['_id']}, {"$push": {"dataflows": dataflow["_id"]}})
            collection = db[DATAFLOWS_COLLECTION_NAME]
            collection.insert_one(dataflow)

        return dataflow["_id"]
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def delete_dataflow(repository_id: str, dataflow_id: str) -> str:
    """
    Method that stores the artifacts (script, requirements, GUI configuration, other metadata)
    """
    try:
        client = MongoClient(os.getenv('DATABASE_URL'))
        db = client[DATABASE_NAME]
        collection = db[REPOSITORIES_COLLECTION_NAME]
        repository = collection.find_one({"_id": repository_id})

        if repository:
            filter = {"_id": repository_id}
            update = {"$pull": {"dataflows": dataflow_id}}
            collection.update_one(filter, update)
            collection = db[DATAFLOWS_COLLECTION_NAME]
            collection.delete_one({"_id": dataflow_id})
        return dataflow_id
    except ConnectionError:
        print("Connection to the MongoDB server failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()


def get_dataflow_field(execution_id, field_name):
    try:
        client = MongoClient(os.environ.get("DATABASE_URL"))
        db = client[DATABASE_NAME]
        collection = db[DATAFLOWS_COLLECTION_NAME]
        execution = collection.find_one({"_id": execution_id}, {field_name: 1})

        if execution:
            return execution.get(field_name)

    except ConnectionError:
        print("Connection to the database failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        client.close()
