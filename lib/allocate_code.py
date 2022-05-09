"""Module containing classes representing the /credit-policies endpoint."""

from flask import request
from flask_restful import Resource, abort
from marshmallow import Schema, fields

from lib.accounts_service import AccountsService, Account
from lib.authorization_service import AuthorizationService, InvalidTokenError
from lib.discount_code import DiscountCodesDataStore, UserCodesDataStore, DiscountCodeNotFound


class AllocateCode(Resource):
    """Class representing the /allocate-code endpoint."""

    class PostRequestSchema(Schema):
        """Schema for validating parameters in POST requests to the endpoint."""
        brand_id = fields.Str()

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
        if account.account_type != Account.TYPE_USER:
            message = "Your account does not have permission to perform the requested action."
            abort(403, message=message)

        brand_id = request.json["brand_id"]
        try:
            discount_code = UserCodesDataStore.find_code(account_id, brand_id)
        except DiscountCodeNotFound:
            try:
                discount_code = DiscountCodesDataStore.allocate_discount_code(brand_id, account_id)
                UserCodesDataStore.add_discount_code(discount_code)
            except DiscountCodeNotFound:
                message = f"There are no codes available for the brand with ID '{brand_id}'."
                return {"message": message}, 200
        return {"discount_code": discount_code.code}, 200
