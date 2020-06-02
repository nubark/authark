from typing import List, Dict, Any
from tenark.resolver import resolve_managers
from .....application.domain.common import QueryDomain
from .tenant_supplier import TenantSupplier



class MemoryTenantSupplier(TenantSupplier):

    def __init__(self) -> None:
        self.arranger, self.provider = resolve_managers({})

    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        return self.provider.get_tenant(tenant_id)

    def create_tenant(self, tenant_dict: Dict[str, Any]) -> None:
        self.arranger.create_tenant(tenant_dict)

    def resolve_tenant(self, name: str) -> Dict[str, Any]:
        return self.provider.resolve_tenant(name)

    def search_tenants(self, domain: QueryDomain) -> List[Dict[str, Any]]:
        return self.provider.search_tenants(domain)
