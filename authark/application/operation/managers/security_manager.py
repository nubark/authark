from typing import List
from ...domain.models import Restriction, Policy
from ...domain.services.repositories import (
    RestrictionRepository, PolicyRepository)
from ...domain.common import RecordList


class SecurityManager:

    def __init__(self, restriction_repository: RestrictionRepository,
                 policy_repository: PolicyRepository,
                 ) -> None:
        self.restriction_repository: RestrictionRepository = (
            restriction_repository)
        self.policy_repository: PolicyRepository = policy_repository

    async def create_restriction(self, entry: dict) -> None:
        meta, data = entry['meta'], entry['data']
        restriction_dicts = data
        restrictions: List[Restriction] = (
            [Restriction(**restriction_dict)
             for restriction_dict in restriction_dicts])
        await self.restriction_repository.add(restrictions)

    async def create_policy(self, entry: dict) -> None:
        meta, data = entry['meta'], entry['data']
        policy_dicts = data
        policies: List[Policy] = [Policy(**policy_dict)
                                  for policy_dict in policy_dicts]
        await self.policy_repository.add(policies)

    async def remove_restriction(self, entry: dict) -> bool:
        meta, data = entry['meta'], entry['data']
        restriction_ids = data
        restrictions = await self.restriction_repository.search(
            [('id', 'in', restriction_ids)])
        return await self.restriction_repository.remove(restrictions)

    async def remove_policy(self, entry: dict) -> bool:
        meta, data = entry['meta'], entry['data']
        policy_ids = data
        policies = await self.policy_repository.search(
            [('id', 'in', policy_ids)])
        return await self.policy_repository.remove(policies)
