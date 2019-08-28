from ....application.models import Dominion
from ....application.utilities import ExpressionParser, TenantProvider
from ....application.repositories import DominionRepository
from .json_repository import JsonRepository


class JsonDominionRepository(JsonRepository[Dominion], DominionRepository):
    """Json Dominion Repository"""

    def __init__(self, file_path: str, parser: ExpressionParser,
                 tenant_provider: TenantProvider,
                 collection_name: str = 'dominions') -> None:
        super().__init__(file_path, parser, tenant_provider,
                         collection_name, Dominion)
