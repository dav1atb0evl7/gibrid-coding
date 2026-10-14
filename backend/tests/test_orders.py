import pytest

from app.models import OrderStatus
from app.services.orders import OrderRequest, validate_order_request


def test_order_request_accepts_bounded_values() -> None:
    validate_order_request(OrderRequest("AI Solution", "Support assistant", "$300–$500", "2 weeks", "@client"))


@pytest.mark.parametrize("field,value", [
    ("service", "  "),
    ("description", "x" * 4001),
    ("contact", ""),
])
def test_order_request_rejects_invalid_field(field: str, value: str) -> None:
    values = {"service": "Web", "description": "Project", "budget": "$100–$300",
              "deadline": "Flexible", "contact": "@client"}
    values[field] = value
    with pytest.raises(ValueError):
        validate_order_request(OrderRequest(**values))


def test_status_lifecycle_is_complete() -> None:
    assert {status.value for status in OrderStatus} == {
        "NEW", "CONTACTED", "NEGOTIATION", "IN_PROGRESS", "COMPLETED", "CANCELLED"
    }
