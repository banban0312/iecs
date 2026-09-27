from functools import lru_cache

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from banban.engine.dialogue_engine import DialogueEngine
from banban.infrastructure import database
from banban.repository.dialogue_state_repository import DialogueStateRepository
from banban.service.dialogue_service import DialogueService
from banban.engine.builder import build_dialogue_engine



async def get_session()->AsyncSession:
    async with database.session_factory() as session:
        yield session

@lru_cache()
def get_dialogue_state_repository(
        session:AsyncSession = Depends(get_session)
)->DialogueStateRepository:
    return DialogueStateRepository(session)

@lru_cache()
def get_dialogue_engine()->DialogueEngine:
   return build_dialogue_engine()

@lru_cache
def get_dialogue_service(
        repository: DialogueStateRepository = Depends(get_dialogue_state_repository),
        engine: DialogueEngine = Depends(get_dialogue_engine),
)->DialogueService:
    return DialogueService(repository,engine)