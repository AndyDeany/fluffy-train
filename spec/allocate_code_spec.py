"""File containing unit tests for the functionality of the /credit-policies endpoint."""
# pylint: disable=invalid-name,line-too-long

from spec.helper import *

from lib.discount_code import DiscountCode, UserCodesDataStore, DiscountCodesDataStore, DiscountCodeNotFound


ENDPOINT_URL = BASE_URL + ALLOCATE_CODE_ENDPOINT_NAME


def generate_test_codes():
    """Generate some discount codes for the test brand for the purposes of testing user codes."""
    requests.post(BASE_URL + GENERATE_CODES_ENDPOINT_NAME,
                  headers=TEST_BRAND_AUTHORIZATION_HEADERS, json={"quantity": 20}).json()


def search_for_user_code():
    """Search for a code that has been allocated to the test user from the test brand.

    Should raise an error if it can't be found.
    """
    UserCodesDataStore.find_code(TEST_USER_ACCOUNT_ID, TEST_BRAND_ACCOUNT_ID)


with description("/allocate-code"):
    with context("valid POST requests"):
        with it("should allocate a code for a valid authorized request from a user account"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(200))
            expect(list(response.json().keys())).to(equal(["discount_code"]))
            allocated_code = DiscountCode(TEST_BRAND_ACCOUNT_ID)
            allocated_code.code = response.json()["discount_code"]
            allocated_code.user_id = TEST_USER_ACCOUNT_ID

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(1))

            expect(available_codes_before_allocation).to(contain(allocated_code))
            expect(available_codes_after_allocation).not_to(contain(allocated_code))

            test_code_is_valid(allocated_code)
            expect(search_for_user_code).not_to(raise_error(DiscountCodeNotFound))

        with it("should return the same code if a repeated authorized request is made"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)

            # Repeated request
            available_codes_before_repeat = get_all_test_brand_codes()
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(200))
            expect(list(response.json().keys())).to(equal(["discount_code"]))
            allocated_code = DiscountCode(TEST_BRAND_ACCOUNT_ID)
            allocated_code.code = response.json()["discount_code"]
            allocated_code.user_id = TEST_USER_ACCOUNT_ID

            available_codes_after_repeat = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_repeat) - len(available_codes_after_repeat)
            expect(codes_removed).to(equal(0))

            expect(available_codes_before_repeat).not_to(contain(allocated_code))

            test_code_is_valid(allocated_code)
            expect(search_for_user_code).not_to(raise_error(DiscountCodeNotFound))

        with it("should return a suitable message if there are no remaining codes"):
            clear_test_codes_from_data_store()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(200))

            expected_message = f"There are no codes available for the brand with ID '{TEST_BRAND_ACCOUNT_ID}'."
            expect(response.json()).to(equal({"message": expected_message}))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))

    with context("invalid POST requests"):
        with it("should not allocate a code for an authorized request from a brand account"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_BRAND_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(403))
            expected_message = "Your account does not have permission to perform the requested action."
            expect(response.json()).to(equal({"message": expected_message}))

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(0))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))

        with it("should not work for a request with an unauthorized token"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            response = requests.post(ENDPOINT_URL, headers=UNAUTHORIZED_HEADERS, json=json)
            expect(response.status_code).to(equal(401))
            expected_message = "Unauthorized. Invalid or expired token."
            expect(response.json()).to(equal({"message": expected_message}))

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(0))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))

        with it("should not work for a request with no authorization token"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
            }
            response = requests.post(ENDPOINT_URL, json=json)
            expect(response.status_code).to(equal(401))
            expected_message = "Unauthorized. Missing authorization token."
            expect(response.json()).to(equal({"message": expected_message}))

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(0))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))

        with it("should return an appropriate 400 message if the 'brand_id' json field is missing"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {}
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Missing json field 'brand_id'."
            expect(response.json()).to(equal({"message": expected_message}))

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(0))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))

        with it("should return an appropriate 400 message an extra json field is given"):
            clear_test_codes_from_data_store()
            generate_test_codes()
            available_codes_before_allocation = get_all_test_brand_codes()
            json = {
                "brand_id": TEST_BRAND_ACCOUNT_ID,
                "planet": "Jupiter",
            }
            response = requests.post(ENDPOINT_URL, headers=TEST_USER_AUTHORIZATION_HEADERS, json=json)
            expect(response.status_code).to(equal(400))
            expected_message = "Bad Request. Unknown field 'planet'."
            expect(response.json()).to(equal({"message": expected_message}))

            available_codes_after_allocation = get_all_test_brand_codes()
            codes_removed = len(available_codes_before_allocation) - len(available_codes_after_allocation)
            expect(codes_removed).to(equal(0))
            expect(search_for_user_code).to(raise_error(DiscountCodeNotFound))
