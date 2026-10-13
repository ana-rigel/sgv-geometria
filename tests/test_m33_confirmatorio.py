import pytest
from experiments import m33_confirmatorio as c
def test_gate_wrong_sha():
    with pytest.raises(SystemExit):c.gate('0'*64)
def test_gate_ok():
    assert c.gate(c.sha(c.PROTO))==c.sha(c.PROTO)
