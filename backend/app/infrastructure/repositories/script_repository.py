"""
Script persistence - sync variant for the Celery task, async for API reads.
"""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.infrastructure.db.models.script import Script


class SyncScriptRepository:
    def __init__(self, session: Session):
        self.session = session

    def mark_processing(self, script: Script) -> None:
        script.status = "processing"
        self.session.commit()

    def mark_done(self, script: Script, *, content_json: dict, model_used: str) -> None:
        script.status = "done"
        script.content_json = content_json
        script.model_used = model_used
        script.error_message = None
        self.session.commit()

    def mark_failed(self, script: Script, *, error_message: str) -> None:
        script.status = "failed"
        script.error_message = error_message[:1000]
        self.session.commit()


class ScriptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pending(self, *, workspace_id: UUID, document_id: UUID, platform: str) -> Script:
        script = Script(workspace_id=workspace_id, document_id=document_id, platform=platform, status="pending")
        self.session.add(script)
        await self.session.commit()
        await self.session.refresh(script)
        return script

    async def get_by_id(self, script_id: UUID) -> Script | None:
        result = await self.session.execute(select(Script).where(Script.id == script_id))
        return result.scalar_one_or_none()

    async def list_by_document(self, document_id: UUID) -> list[Script]:
        result = await self.session.execute(
            select(Script).where(Script.document_id == document_id).order_by(Script.created_at.desc())
        )
        return list(result.scalars().all())