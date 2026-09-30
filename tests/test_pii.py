from app.logging_config import scrub_event
from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_vietnamese_identity_card_number() -> None:
    out = scrub_text("CCCD: 079123456789")
    assert "079123456789" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card_number_with_spaces() -> None:
    out = scrub_text("Card: 4111 1111 1111 1111")
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_log_scrubber_covers_all_nested_string_fields() -> None:
    record = {
        "event": "request_failed",
        "detail": "Contact student@vinuni.edu.vn",
        "payload": {"nested": ["Call 090 123 4567"]},
    }

    scrubbed = scrub_event(None, "error", record)

    assert "student@vinuni.edu.vn" not in str(scrubbed)
    assert "090 123 4567" not in str(scrubbed)
    assert "REDACTED_EMAIL" in str(scrubbed)
    assert "REDACTED_PHONE_VN" in str(scrubbed)
