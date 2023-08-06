import pytest

from am4utils.api import fetch_alliance
from am4utils.log import AllianceLog, UserLog

@pytest.mark.asyncio
async def test_alliance_log():
    status, log0 = await fetch_alliance(None, "src/am4utils/tests/data/A_Valiant Air_1691065293.json")
    log1 = AllianceLog.from_log_id(log0.log_id)
    assert status.success is True
    assert log1.log_id == log0.log_id
    assert len(log1.members) == len(log0.members)
    for m0, m1 in zip(log0.members, log1.members):
        assert m0.username == m1.username