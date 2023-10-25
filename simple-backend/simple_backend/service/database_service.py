import os

def get_database():
    db_type = os.environ.get("DATABASE_TYPE", "MONGODB")
    if db_type == "MONGODB":
        from simple_backend.databases.mongodb import MongoDB
        MONGODB_URL=os.getenv('MONGODB_URL')
        return MongoDB(MONGODB_URL)

class DatabaseService:
    def create_document(self, collection_id: str, document):
        pass


    def get_document(self, collection_id: str, filter: dict, projection: dict = {}):
        pass


    def delete_document(self, collection_id: str, document_id: str):
        pass
            

    def get_document_field(self, collection_id: str, document_id: str, field_name: str):
        pass


    def set_document_field(self, collection_id: str,  document_id: str, field_name: str, field_value: str):
        pass


    def push_document_array_field(self, collection_id: str,document_id: str, field_name: str, field_value: str):
        pass
        

    def get_all_documents_fields(self, collection_id: str, projection: dict):
        pass


    def watch_document(self, collection_id: str, update_function):
        pass


    def watch_documents(self, collection_id: str, update_function):
        pass