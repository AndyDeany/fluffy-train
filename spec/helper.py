"""File containing general information shared between multiple tests."""

import json
import re as _re
from mamba import description, context, it
from expects import expect, equal, be, contain, raise_error
import requests

from lib.discount_code import DiscountCodesDataStore, UserCodesDataStore


BASE_URL = "http://127.0.0.1:5000"
GENERATE_CODES_ENDPOINT_NAME = "/generate-codes"
ALLOCATE_CODE_ENDPOINT_NAME = "/allocate-code"

TEST_BRAND_ACCOUNT_ID = "1ec1e6bc-7906-4859-8edc-eddf6185ced8"
TEST_BRAND_AUTHORIZATION_HEADERS = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}

TEST_USER_ACCOUNT_ID = "c1d415ed-0d22-4fed-8235-c76e9d69be17"
TEST_USER_AUTHORIZATION_HEADERS = {"Authorization": "Bearer SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVQa"}

UNAUTHORIZED_HEADERS = {"Authorization": "Bearer eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6"}

INVALID_CODE_CHARACTER_REGEX = r"[^ABCDEFGHJKMNPQRTUVWXY346789]"


def test_code_is_valid(discount_code):
    """Test that the given DiscountCode object is valid."""
    expect(len(discount_code.code)).to(equal(12))
    expect(_re.search(INVALID_CODE_CHARACTER_REGEX, discount_code.code)).to(be(None))
    expect(discount_code.brand_id).to(equal(TEST_BRAND_ACCOUNT_ID))


def get_all_brand_codes(brand_id):
    """Return all discount codes from the data store that are associated with the given brand."""
    test_brand_codes = []
    DiscountCodesDataStore.read_from_json()
    for code in DiscountCodesDataStore.codes:
        if code.brand_id == brand_id:
            test_brand_codes.append(code)
    return test_brand_codes


def get_all_test_brand_codes():
    """Return all discount codes from the data store that are associated with the test brand."""
    return get_all_brand_codes(TEST_BRAND_ACCOUNT_ID)


def clear_test_codes_from_data_store():
    """Purge all discount codes from the data store that are associated with the test brand/user.

    This ensures a blank slate before running tests.
    """
    for code in get_all_test_brand_codes():
        DiscountCodesDataStore.remove_discount_code(code)

    codes_to_remove = []
    for code in UserCodesDataStore.codes:
        if code.brand_id == TEST_BRAND_ACCOUNT_ID and code.user_id == TEST_USER_ACCOUNT_ID:
            codes_to_remove.append(code)
    for code in codes_to_remove:
        UserCodesDataStore.remove_discount_code(code)
