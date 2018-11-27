import json
import jwt
from pytest import fixture
from flask import Flask
from authark.application.models.user import User
from authark.application.models.credential import Credential
from authark.application.repositories.user_repository import (
    MemoryUserRepository)
from authark.application.repositories.credential_repository import (
    MemoryCredentialRepository)
from authark.application.repositories.expression_parser import ExpressionParser
from authark.application.coordinators.auth_coordinator import AuthCoordinator
from authark.application.services.hash_service import MemoryHashService
from authark.infrastructure.config.registry import Registry
from authark.infrastructure.web.base import create_app
from authark.infrastructure.config.config import TrialConfig
from authark.infrastructure.config.context import Context

from authark.infrastructure.crypto.pyjwt_token_service import PyJWTTokenService


class MockRegistry(Registry):

    def __init__(self) -> None:
        parser = ExpressionParser()
        user_repository = MemoryUserRepository(parser)
        credential_repository = MemoryCredentialRepository(parser)
        user_repository.load({
            '1': User(
                id="1",
                username="eecheverry",
                email="eecheverry@nubark.com"),
            '2': User(
                id="2",
                username="mvivas",
                email="mvivas@gmail.com"
            )
        })
        refresh_token = jwt.encode(
            {'user': "pepe"}, 'REFRESHSECRET').decode('utf-8')
        credential_repository.load({
            "1": Credential(id='1', user_id='1', value="HASHED: ABC1234"),
            "2": Credential(id='2', user_id='2', value="HASHED: XYZ098"),
            "3": Credential(id='3', user_id='1', value=refresh_token,
                            type='refresh_token'),
        })
        access_token_service = PyJWTTokenService('TESTSECRET', 'HS256', 3600)
        refresh_token_service = PyJWTTokenService(
            'REFRESHSECRET', 'HS256', 3600, 3600)
        hash_service = MemoryHashService()
        auth_coordinator = AuthCoordinator(
            user_repository, credential_repository,
            hash_service, access_token_service,
            refresh_token_service)

        self['auth_coordinator'] = auth_coordinator


@fixture
def app() -> Flask:
    """Create app testing client"""
    config = TrialConfig()
    mock_registry = MockRegistry()
    context = Context(config, mock_registry)

    app = create_app(context=context)
    app.testing = True
    app = app.test_client()

    return app


def test_auth_get_route(app: Flask) -> None:
    response = app.get('/auth')
    expected_response = (b"Authentication endpoint. "
                         b"Please 'Post' to '/auth'")
    assert expected_response in response.get_data()


def test_auth_post_route_failed_authentication(app: Flask) -> None:
    response = app.post(
        '/auth',
        data=json.dumps(dict(
            username="Esteban",
            password="ABC1234"
        )),
        content_type='application/json')
    expected_response = b''
    assert expected_response in response.get_data()


def test_auth_post_route_successful_authentication(app: Flask) -> None:
    response = app.post(
        '/auth',
        data=json.dumps(dict(
            username="eecheverry",
            password="ABC1234",
            client="mobile"
        )),
        content_type='application/json')
    assert response.status_code == 200
    data = response.get_data()
    assert len(data) > 0


def test_auth_post_route_with_refresh_token(app: Flask) -> None:
    token = jwt.encode(
        {'user': "pepe"}, 'REFRESHSECRET').decode('utf-8')
    response = app.post(
        '/auth',
        data=json.dumps(dict(
            refresh_token=token
        )),
        content_type='application/json')
    assert response.status_code == 200
    data = response.get_data()
    assert len(data) > 0


def test_register_post_route(app: Flask) -> None:
    response = app.post(
        '/register',
        data=json.dumps(dict(
            username="gecheverry",
            email="gecheverry@gmail.com",
            password="POI123"
        )),
        content_type='application/json')

    assert response.status_code == 201
    assert b"username<gecheverry>" in response.get_data()
    assert b"email<gecheverry@gmail.com>" in response.get_data()
