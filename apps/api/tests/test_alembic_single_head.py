from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory



def test_alembic_has_single_head() -> None:
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    script = ScriptDirectory.from_config(config)

    heads = script.get_heads()

    assert len(heads) == 1, f"Expected exactly one Alembic head, found {len(heads)}: {heads}"
