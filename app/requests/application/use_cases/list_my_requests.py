"""Query: Listar mis solicitudes de tiempo libre"""
from dataclasses import dataclass
from typing import List
from app.requests.application.ports.time_off_request_repository import TimeOffRequestRepository
from app.requests.domain.time_off_request import TimeOffRequest

@dataclass
class ListMyRequestsCommand:
    user_id: str
    limit: int = 50

class ListMyRequestsUseCase:
    def __init__(self, request_repository: TimeOffRequestRepository):
        self.request_repository = request_repository

    async def execute(self, cmd: ListMyRequestsCommand) -> List[TimeOffRequest]:
        return await self.request_repository.find_by_user(cmd.user_id, cmd.limit)
