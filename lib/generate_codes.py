"""Module containing classes representing the /credit-policies endpoint."""

from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields

from lib.accounts_service import AccountsService, Account
from lib.authorization_service import AuthorizationService, InvalidTokenError
from lib.discount_code import DiscountCode, DiscountCodesDataStore


class GenerateCodes(Resource):
    """Class representing the /generate-codes endpoint."""

    class PostRequestSchema(Schema):
        """Schema for validating parameters in POST requests to the endpoint."""
        quantity = fields.Int()

    POST_REQUEST_SCHEMA = PostRequestSchema()

    def post(self):
        """Request generation of new discount codes."""
        errors = self.POST_REQUEST_SCHEMA.validate(request.json)
        if errors:
            message = "Bad Request."
            for error in errors:
                message += f" Unknown field '{error}'."
            abort(400, message=message)

        expected_fields = self.POST_REQUEST_SCHEMA.declared_fields.keys()
        missing_fields = sorted([f for f in expected_fields if f not in request.json])
        print(expected_fields)
        print(missing_fields)
        if missing_fields:
            message = "Missing json field"
            if len(missing_fields) > 1:
                message += "s"
            message += " {}.".format(", ".join("'{}'".format(f) for f in missing_fields))
            abort(400, message=message)

        try:
            account_id = AuthorizationService.validate_token(request.headers["Authorization"])
        except InvalidTokenError:
            abort(401, message="Unauthorized. Invalid or expired token.")
        except KeyError:
            abort(401, message="Unauthorized. Missing authorization token.")

        account = AccountsService.get_account_by_id(account_id)
        if account.account_type != Account.TYPE_BRAND:
            message = "Your account does not have permission to perform the requested action."
            abort(403, message=message)

        for _ in range(request.json["quantity"]):
            DiscountCodesDataStore.add_discount_code(DiscountCode(account_id))

        return {}, 200
