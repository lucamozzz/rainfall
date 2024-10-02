from pymongo import MongoClient
from service.database_service import DatabaseService
from json import dumps

DATABASE_NAME='rainfall'
EXECUTIONS_COLLECTION_NAME='executions'


class MongoDB(DatabaseService):
    def __init__(self, connection_string: str):
        self.client = MongoClient(connection_string)
        self.db = self.client[DATABASE_NAME]

    def create_document(self, collection_id: str, document: dict):
        try:
            collection = self.db[collection_id]
            collection.insert_one(document)
        except ConnectionError:
            print("Connection to the MongoDB server failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def get_document(self, collection_id: str, filter: dict, projection: dict = {}):
        try:
            collection = self.db[collection_id]
            return collection.find_one(filter, projection)
            
        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def delete_document(self, collection_id: str, document_id: str):
        try:
            collection = self.db[collection_id]
            collection.delete_one({"_id": document_id})
            
        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            

    def get_document_field(self, collection_id: str, document_id: str, field_name: str):
        try:
            collection = self.db[collection_id]
            document = collection.find_one({"_id": document_id}, {field_name: 1})

            if document:
                return document.get(field_name)

        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def set_document_field(self, collection_id: str,  document_id: str, field_name: str, field_value: str):
        try:
            collection = self.db[collection_id]
            document = collection.find_one({"_id": document_id})
            if document:
                collection.update_one({"_id": document_id}, {"$set": {field_name: field_value}})
            
        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def push_document_array_field(self, collection_id: str, document_id: str, field_name: str, field_value: str):
        try:
            collection = self.db[collection_id]
            collection.update_one({"_id": document_id}, {"$push": {field_name: field_value}})

        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def pull_document_array_field(self, collection_id: str, document_id: str, field_name: str, field_value: str):
        try:
            collection = self.db[collection_id]
            collection.update_one({"_id": document_id}, {"$pull": {field_name: field_value}})

        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        

    def get_all_documents_fields(self, collection_id: str, projection: dict, filter: dict = {}):
        try:
            collection = self.db[collection_id]
            documents = list(collection.find(filter, projection))
            result = []
            for document in documents:
                output_doc = {}
                for key in projection.keys():
                    if(key == "_id"):
                        output_doc["id"] = str(document[key])
                    else:
                        output_doc[key] = str(document[key])
                result.append(output_doc)
            return result

        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")


    def watch_document(self, collection_id: str, update_function):    
        try:
            collection = self.db[collection_id]
            pipeline = [{'$match': {'operationType': 'update'}}]
            with collection.watch(pipeline) as stream:
                for change in stream:
                    document_update = change["updateDescription"]["updatedFields"]
                    yield update_function(document_update)

        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e.with_traceback)}")


    def watch_documents(self, collection_id: str, update_function):
        try:
            collection = self.db[collection_id]
            pipeline = [{'$match': {'operationType': 'update'}}]
            with collection.watch(pipeline) as stream:
                for change in stream:
                    pipeline_id = str(change["documentKey"]["_id"])
                    updated_document = change["updateDescription"]["updatedFields"]
                    yield update_function(updated_document, pipeline_id)
        
        except ConnectionError:
            print("Connection to the database failed.")
        except Exception as e:
            print(f"An error occurred: {str(e.with_traceback)}")