from typing import Dict, cast, List
from pytest import fixture, raises
from authark.application.coordinators.auth_coordinator import AuthCoordinator
from authark.application.utilities import (
    QueryParser, UserCreationError, AuthError, RecordList)
from authark.application.repositories.memory_model_repositories import (
    UserRepository, MemoryUserRepository,
    CredentialRepository, MemoryCredentialRepository)
from authark.application.services.token_service import (
    TokenService, MemoryTokenService)
from authark.application.services.hash_service import (
    HashService, MemoryHashService)
from authark.application.models import User, Credential, Token


########
# TESTS
########
def test_auth_coordinator_creation(
        auth_coordinator: AuthCoordinator) -> None:
    assert hasattr(auth_coordinator, 'authenticate')


async def test_auth_coordinator_authenticate(
        auth_coordinator: AuthCoordinator) -> None:

    tokens = await auth_coordinator.authenticate("tebanep", "PASS2", 'mobile')

    assert isinstance(tokens, dict)
    assert 'refresh_token' in tokens.keys()
    assert 'access_token' in tokens.keys()


async def test_auth_coordinator_find_user_by_email(
        auth_coordinator: AuthCoordinator) -> None:

    user = await auth_coordinator._find_user("tebanep@gmail.com")

    assert isinstance(user, User)
    assert user.id == '2'


async def test_auth_coordinator_find_user(
        auth_coordinator: AuthCoordinator) -> None:

    user = await auth_coordinator._find_user("tebanep")

    assert isinstance(user, User)
    assert user.id == '2'


async def test_auth_coordinator_authenticate_no_credentials(
        auth_coordinator: AuthCoordinator) -> None:
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default'] = {}
    with raises(AuthError):
        tokens = await auth_coordinator.authenticate(
            "tebanep", "PASS2", 'mobile')


async def test_auth_coordinator_refresh_authenticate_no_renewal(
        auth_coordinator: AuthCoordinator) -> None:
    user_id = '1'
    refresh_token = "PREVIOUS_TOKEN"
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default']['4'] = Credential(
        id='4', user_id=user_id, value=refresh_token, type='refresh_token')

    tokens = await auth_coordinator.refresh_authenticate(refresh_token)

    assert isinstance(tokens, dict)
    assert 'access_token' in tokens.keys()
    assert 'refresh_token' not in tokens.keys()


async def test_auth_coordinator_refresh_authenticate_renewal(
        auth_coordinator: AuthCoordinator, monkeypatch) -> None:

    user_id = '1'
    refresh_token = "PREVIOUS_TOKEN"
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default']['4'] = Credential(
        id='4', user_id=user_id, value=refresh_token, type='refresh_token')

    auth_coordinator.refresh_token_service.renew = (  # type: ignore
        lambda token: True)

    tokens = await auth_coordinator.refresh_authenticate(refresh_token)

    assert isinstance(tokens, dict)
    assert 'access_token' in tokens.keys()
    assert 'refresh_token' in tokens.keys()


async def test_auth_coordinator_refresh_authenticate_refresh_token_not_found(
        auth_coordinator: AuthCoordinator) -> None:
    user_id = '1'
    refresh_token = "GOOD_TOKEN"
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default']['4'] = Credential(
        id='4', user_id=user_id, value=refresh_token, type='refresh_token')

    with raises(AuthError):
        tokens = await auth_coordinator.refresh_authenticate("BAD_TOKEN")


async def test_generate_refresh_token(
        auth_coordinator: AuthCoordinator) -> None:
    user_id = '1'
    client = 'mobile'
    refresh_token = await auth_coordinator._generate_refresh_token(
        user_id, client)
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)

    assert isinstance(refresh_token, str)
    assert len(credential_repository.data['default']) == 4


async def test_generate_refresh_token_only_one(
        auth_coordinator: AuthCoordinator) -> None:
    user_id = '1'
    client = 'mobile'
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default']['4'] = Credential(
        id='4', user_id=user_id, value="PREVIOUS_TOKEN", type='refresh_token',
        client=client)

    assert len(credential_repository.data['default']) == 4
    refresh_token = await auth_coordinator._generate_refresh_token(
        user_id, client)
    assert isinstance(refresh_token, str)
    assert len(credential_repository.data['default']) == 4


async def test_auth_coordinator_fail_to_authenticate(
        auth_coordinator: AuthCoordinator) -> None:

    with raises(AuthError):
        token = await auth_coordinator.authenticate("tebanep", "WRONG_PASSWORD",
                                                    'web')


async def test_auth_coordinator_fail_to_authenticate_missing_user(
        auth_coordinator: AuthCoordinator) -> None:

    with raises(AuthError):
        token = await auth_coordinator.authenticate(
            "MISSING_USER", "WRONG_PASSWORD", "web")


async def test_auth_coordinator_fail_to_authenticate_missing_credentials(
        auth_coordinator: AuthCoordinator) -> None:
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    credential_repository.data['default'] = {}

    with raises(AuthError):
        token = await auth_coordinator.authenticate("tebanep", "NO_CREDENTIALS",
                                                    'terminal')


async def test_auth_coordinator_register(
        auth_coordinator: AuthCoordinator) -> None:

    user_dicts: RecordList = [{
        "username": "mvp",
        "email": "mvp@gmail.com",
        "password": "PASS4"
    }]
    user_dicts = await auth_coordinator.register(user_dicts)
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    user_repository = cast(MemoryUserRepository,
                           auth_coordinator.user_repository)
    assert user_dicts
    assert isinstance(user_dicts, List)
    assert len(user_repository.data['default']) == 4
    assert len(credential_repository.data['default']) == 4


async def test_auth_coordinator_register_username_special_characters_error(
        auth_coordinator: AuthCoordinator) -> None:
    with raises(UserCreationError):
        user_dicts: RecordList = [{
            "username": "mvp@gmail.com",
            "email": "mvp@gmail.com",
            "password": "PASS4"
        }]
        await auth_coordinator.register(user_dicts)


async def test_auth_coordinator_register_duplicated_email_error(
        auth_coordinator: AuthCoordinator) -> None:
    try:
        user_dicts: RecordList = [{
            "username": "mvp",
            "email": "mvp@gmail.com",
            "password": "PASS4"
        }]
        await auth_coordinator.register(user_dicts)
        user_dicts[0]['username'] = "mvp2"
        user_dicts[0]['email'] = "mvp@gmail.com"
        await auth_coordinator.register(user_dicts)
    except UserCreationError as e:
        assert "email" in str(e)


async def test_auth_coordinator_register_duplicated_username_error(
        auth_coordinator: AuthCoordinator) -> None:
    try:
        user_dicts: RecordList = [{
            "username": "mvp",
            "email": "mvp@gmail.com",
            "password": "PASS4"
        }]
        await auth_coordinator.register(user_dicts)
        user_dicts[0]['username'] = "mvp"
        user_dicts[0]['email'] = "mvp2@gmail.com"
        await auth_coordinator.register(user_dicts)
    except UserCreationError as e:
        assert "username" in str(e)


async def test_auth_coordinator_deregister(
        auth_coordinator: AuthCoordinator, mock_user_repository) -> None:

    user = await mock_user_repository.search(
        [('id', '=', '2')])
    unregistered = await auth_coordinator.deregister(user[0].id)
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    user_repository = cast(MemoryUserRepository,
                           auth_coordinator.user_repository)

    assert unregistered is True
    assert len(user_repository.data['default']) == 2
    assert len(credential_repository.data['default']) == 2


async def test_auth_coordinator_deregister_without_ids(
        auth_coordinator: AuthCoordinator, mock_user_repository) -> None:

    user_id = ''
    unregistered = await auth_coordinator.deregister(user_id)
    credential_repository = cast(MemoryCredentialRepository,
                                 auth_coordinator.credential_repository)
    user_repository = cast(MemoryUserRepository,
                           auth_coordinator.user_repository)

    assert unregistered is False
    assert len(user_repository.data['default']) == 3
    assert len(credential_repository.data['default']) == 3


async def test_make_password_credential(
        auth_coordinator: AuthCoordinator) -> None:
    user_id='2'
    user_password=""
    await auth_coordinator._make_password_credential(user_id,user_password)
