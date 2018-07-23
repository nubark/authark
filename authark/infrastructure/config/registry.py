from collections import UserDict
from typing import Any, Dict
from abc import ABC, abstractmethod
from authark.application.models.user import User
from authark.application.coordinators.auth_coordinator import AuthCoordinator
from authark.application.repositories.user_repository import (
    MemoryUserRepository)
from authark.infrastructure.crypto.pyjwt_token_service import PyJWTTokenService
from authark.infrastructure.data.json_user_repository import (
    JsonUserRepository)
from authark.infrastructure.config.config import Config


class Registry(dict, ABC):
    @abstractmethod
    def __init__(self, config: Config):
        pass


class MemoryJwtRegistry(Dict[str, Any]):

    def __init__(self, config: Config) -> None:

        # Services
        user_repository = MemoryUserRepository()
        token_service = PyJWTTokenService('DEVSECRET123', 'HS256')
        auth_coordinator = AuthCoordinator(user_repository, token_service)

        self['auth_coordinator'] = auth_coordinator


class JsonJwtRegistry(Dict[str, Any]):

    def __init__(self, config: Config) -> None:
        database_config = config.get("database")
        database_path = database_config.get("url")

        # Services
        user_repository = JsonUserRepository(database_path)
        token_service = PyJWTTokenService('DEVSECRET123', 'HS256')
        auth_coordinator = AuthCoordinator(user_repository, token_service)

        self['auth_coordinator'] = auth_coordinator
