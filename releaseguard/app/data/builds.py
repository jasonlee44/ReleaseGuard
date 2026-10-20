from app.schemas.build import Build

BUILDS: dict[str, Build] = {}

def reset_builds() -> None:
    BUILDS.clear()
