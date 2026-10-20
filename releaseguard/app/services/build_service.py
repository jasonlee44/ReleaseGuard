from datetime import datetime, timezone
from app.schemas.build import Build, BuildCreate
from app.data.builds import BUILDS
from uuid import uuid4

def create_build(payload: BuildCreate) -> Build:
    new_build=Build(
        build_id=uuid4(),
        name=payload.name,
        version=payload.version,
        description=payload.description,
        created_at=datetime.now(timezone.utc)
    )
    BUILDS[str(new_build.build_id)] = new_build

    return new_build


def list_builds() -> list[Build]:
    return list(BUILDS.values())