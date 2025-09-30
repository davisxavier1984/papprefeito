"""
Cliente Appwrite configurado para o sistema MaisPAP
"""
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.services.storage import Storage
from app.core.config import settings


class AppwriteClient:
    """Singleton para cliente Appwrite"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        """Inicializa cliente Appwrite"""
        self.client = Client()
        self.client.set_endpoint(settings.APPWRITE_ENDPOINT)
        self.client.set_project(settings.APPWRITE_PROJECT_ID)
        self.client.set_key(settings.APPWRITE_API_KEY)

        # Serviços disponíveis
        self.databases = Databases(self.client)
        self.users = Users(self.client)
        self.storage = Storage(self.client)

    def get_client(self) -> Client:
        """Retorna instância do client"""
        return self.client

    def get_databases(self) -> Databases:
        """Retorna serviço de databases"""
        return self.databases

    def get_users(self) -> Users:
        """Retorna serviço de users"""
        return self.users

    def get_storage(self) -> Storage:
        """Retorna serviço de storage"""
        return self.storage


# Instância global do cliente
appwrite_client = AppwriteClient()
