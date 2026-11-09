from app.schemas.test_run import TestRun

TEST_RUNS: dict[str, TestRun] = {}

def reset_test_runs() -> None:
    TEST_RUNS.clear()
