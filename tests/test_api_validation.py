import pytest
from pydantic import ValidationError

from web.app import AdviceRequest


def test_advice_request_strips_title():
    request = AdviceRequest(title="  test  ", proposed_price=100)
    assert request.title == "test"

def test_advice_request_rejects_empty_title():
    # pytest.raises = raises an exception and verifies it was raised, error is expected
    with pytest.raises(ValidationError):
        AdviceRequest(title="", proposed_price=100)

def test_advice_request_rejects_negative_price():
    with pytest.raises(ValidationError):
        AdviceRequest(title="test", proposed_price=-100)

def test_advice_request_rejects_extra_fields():
    with pytest.raises(ValidationError):
        AdviceRequest(title="test", proposed_price=100, unexpected="dhomini lixo...")