### Running the API and tests
* Create a Python virtual environment in the main folder of the repo (`python -m venv venv`).
* Activate this virtual environment
  (`source venv/bin/activate` on UNIX, `.\venv\Scripts\activate\` on Windows).
* Install requirements (`python -m pip install -r test-requirements.txt`).
  If you just want to run the API and not the tests, you can just install `requirements.txt` instead.
* To run the API, use `python main.py`.
* To run the tests, in a separate window run `mamba --format=documentation`.

To test the API manually you can use:

POST `http://127.0.0.1:5000/generate-codes` with headers:
`{"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"}` and json payload:
`{"quantity": 15}` (or any number you like).

or

POST `http://127.0.0.1:5000/allocate-code` with headers:
`{"Authorization": "Bearer SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVQa"}` and json payload:
`{"brand_id": 1ec1e6bc-7906-4859-8edc-eddf6185ced8}`.


### Documentation

#### `/generate-codes`

This endpoint allows a brand to generate a given amount of discount codes which will
be made available to users.

An "Authorization" header is required with a valid Bearer token.
The json payload must contain one field, "quantity",
which should be an integer greater than 0.

This returns 200 OK if successful, with no JSON payload.

A 401 Unauthorized is returned if the authorization header is missing or invalid.

A 403 Forbidden is returned if the request is made from an account that is not a brand account.

---

#### `/allocate-code`

This endpoint allows a user to be allocated a discount code in exchange
for their contact information being shared with the brand that supplied it.

An "Authorization" header is required with a valid Bearer token.
The json payload must contain one field, "brand_id",
which should be a valid brand UUID.

This returns 200 OK if successful, and includes a "discount_code" field
in the returned json payload containing the discount code.


A 401 Unauthorized is returned if the authorization header is missing or invalid.

A 403 Forbidden is returned if the request is made from an account that is not a user account.
