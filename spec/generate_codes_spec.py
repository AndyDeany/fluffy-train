"""File containing unit tests for the functionality of the /credit-policies endpoint."""
# pylint: disable=invalid-name,line-too-long

from spec.helper import *


ENDPOINT_NAME = "/generate-codes"
ENDPOINT_URL = BASE_URL + ENDPOINT_NAME


with description("/generate-codes"):
    with context("valid POST requests"):
        with it("should create codes for a valid authorized request from a brand account"):
            clear_test_codes_from_data_store()
            creation_quantity = 20
            json = {
                "quantity": creation_quantity,
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(200))
            created_codes = get_all_test_brand_codes()
            expect(len(created_codes)).to(equal(creation_quantity))
            for discount_code in created_codes:
                test_code_is_valid(discount_code)
                expect(discount_code.user_id).to(equal(None))

    with context("invalid POST requests"):
        with it("should not create codes for an authorized request from a user account"):
            clear_test_codes_from_data_store()
            json = {
                "quantity": 50,
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
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
            json = {}
            response = requests.post(ENDPOINT_URL, headers=TEST_BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Missing json field 'quantity'."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(len(get_all_test_brand_codes())).to(equal(0))

        with it("should return an appropriate 400 message an extra json field is given"):
            json = {
                "quantity": 12,
                "planet": "Mars",
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Bad Request. Unknown field 'planet'."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(len(get_all_test_brand_codes())).to(equal(0))
