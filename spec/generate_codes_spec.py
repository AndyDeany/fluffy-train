"""File containing unit tests for the functionality of the /credit-policies endpoint."""
# pylint: disable=invalid-name,line-too-long

from expects import expect, equal
from mamba import description, context, it
import requests

from spec.helper import (BASE_URL, TEST_BRAND_ACCOUNT_ID, TEST_BRAND_BEARER_TOKEN,
                         TEST_USER_ACCOUNT_ID, TEST_USER_BEARER_TOKEN)

from lib.discount_code import DiscountCodesDataStore


def get_all_brand_codes(brand_id):
    """Return all discount codes from the data store that are associated with the given brand."""
    test_brand_codes = []
    for code in DiscountCodesDataStore.codes:
        if code.brand_id == brand_id:
            test_brand_codes.append(code)
    return test_brand_codes


def get_all_test_brand_codes():
    """Return all discount codes from the data store that are associated with the test brand."""
    return get_all_brand_codes(TEST_BRAND_ACCOUNT_ID)


def clear_test_codes_from_data_store():
    """Purge all discount codes from the data store that are associated with the test brand.

    This ensures a blank slate before running tests.
    """
    for code in get_all_test_brand_codes():
        DiscountCodesDataStore.codes.remove(code)


ENDPOINT_NAME = "/generate-codes"
ENDPOINT_URL = BASE_URL + ENDPOINT_NAME

BRAND_AUTHORIZATION_HEADERS = {"Authorization": TEST_BRAND_BEARER_TOKEN}
USER_AUTHORIZATION_HEADERS = {"Authorization": TEST_USER_BEARER_TOKEN}
UNAUTHORIZED_HEADERS = {"Authorization": "Bearer eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6"}


with description(ENDPOINT_NAME):
    with context("valid POST requests"):
        with it("should create codes for a valid authorized request from a brand account"):
            clear_test_codes_from_data_store()
            creation_quantity = 20
            json = {
                "quantity": creation_quantity,
            }
            response = requests.post(ENDPOINT_URL, headers=BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(200))
            expect(len(get_all_test_brand_codes())).to(equal(creation_quantity))

    with context("invalid POST requests"):
        with it("should not create codes for an authorized request from a user account"):
            clear_test_codes_from_data_store()
            json = {
                "quantity": 50,
            }
            response = requests.post(ENDPOINT_URL, headers=USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(403))
            expected_message = "Your account does not have permission to perform the requested action."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(len(get_all_brand_codes(TEST_USER_ACCOUNT_ID))).to(equal(0))

        with it("should not work for a request with an unauthorized token"):
            clear_test_codes_from_data_store()
            json = {
                "quantity": 80,
            }
            response = requests.post(ENDPOINT_URL, headers=UNAUTHORIZED_HEADERS, json=json)
            expect(response.status_code).to(equal(401))
            expected_message = "Unauthorized. Invalid or expired token."
            expect(response.json()).to(equal({"message": expected_message}))

        with it("should not work for a request with no authorization token"):
            clear_test_codes_from_data_store()
            json = {
                "quantity": 80,
            }
            response = requests.post(ENDPOINT_URL, json=json)
            expect(response.status_code).to(equal(401))
            expected_message = "Unauthorized. Missing authorization token."
            expect(response.json()).to(equal({"message": expected_message}))

        with it("should return an appropriate 400 message if the quantity json field is missing"):
            clear_test_codes_from_data_store()
            json = {
                "quantity": 50,
            }
            response = requests.post(ENDPOINT_URL, headers=BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Missing json field 'quantity'."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(len(get_all_test_brand_codes())).to(equal(0))

        with it("should return an appropriate 400 message an extra json field is given"):
            json = {
                "quantity": 12,
                "planet": "Mars",
            }
            response = requests.post(ENDPOINT_URL, headers=BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Bad Request. Unknown field 'planet'."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(len(get_all_test_brand_codes())).to(equal(0))
