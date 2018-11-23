from pytest import fixture, raises
from authark.application.models import User, Credential, Dominion, Role
from authark.application.repositories import (
    ExpressionParser,
    UserRepository, MemoryUserRepository,
    CredentialRepository, MemoryCredentialRepository,
    DominionRepository, MemoryDominionRepository,
    RoleRepository, MemoryRoleRepository)
from authark.application.reporters.authark_reporter import (
    AutharkReporter, StandardAutharkReporter)


@fixture
def user_repository() -> UserRepository:
    parser = ExpressionParser()
    user_repository = MemoryUserRepository(parser)
    user_repository.load({
        "valenep": User(id='1', username='valenep', email='valenep@gmail.com'),
        "tebanep": User(id='2', username='tebanep', email='tebanep@gmail.com'),
        "gabeche": User(id='3', username='gabeche', email='gabeche@gmail.com')
    })
    return user_repository


@fixture
def credential_repository() -> CredentialRepository:
    credentials_dict = {
        "1": Credential(id='1', user_id='1', value="PASS1"),
        "2": Credential(id='2', user_id='2', value="PASS2"),
        "3": Credential(id='3', user_id='3', value="PASS3"),
    }
    parser = ExpressionParser()
    credential_repository = MemoryCredentialRepository(parser)
    credential_repository.load(credentials_dict)
    return credential_repository


@fixture
def dominion_repository() -> DominionRepository:
    dominions_dict = {
        "1": Dominion(id='1', name='Data Server',
                      url="https://dataserver.nubark.com")
    }
    parser = ExpressionParser()
    dominion_repository = MemoryDominionRepository(parser)
    dominion_repository.load(dominions_dict)
    return dominion_repository


@fixture
def role_repository() -> RoleRepository:
    roles_dict = {
        "1": Role(id='1', name='admin', dominion_id='1',
                  description="Service's Administrator")
    }
    parser = ExpressionParser()
    role_repository = MemoryRoleRepository(parser)
    role_repository.load(roles_dict)
    return role_repository


@fixture
def authark_reporter(
        user_repository, credential_repository,
        dominion_repository, role_repository) -> AutharkReporter:
    return StandardAutharkReporter(user_repository, credential_repository,
                                   dominion_repository, role_repository)
