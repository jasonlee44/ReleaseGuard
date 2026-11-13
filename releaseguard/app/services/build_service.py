from datetime import datetime, timezone
from app.schemas.build import Build, BuildCreate
from uuid import uuid4
from sqlalchemy import select
from app.db.database import SessionLocal
from app.db import models

def create_build(payload: BuildCreate) -> Build:
    new_build=models.Build(
        build_id=uuid4(),
        name=payload.name,
        version=payload.version,
        description=payload.description,
        created_at=datetime.now(timezone.utc)
    )

    with SessionLocal() as session:
        session.add(new_build)
        session.commit()
        
        return Build(
            build_id=new_build.build_id,
            name=new_build.name,
            version=new_build.version,
            description=new_build.description,
            created_at=new_build.created_at
            )


def list_builds() -> list[Build]:
    with SessionLocal() as session:
        rows = session.scalars(select(models.Build)).all()
        return [
            Build(
                build_id=row.build_id,
                name=row.name,
                version=row.version,
                description=row.description,
                created_at=row.created_at
            )
            for row in rows
        ]