"""Module for managing interactions with accounts and the Accounts Microservice."""


class Account:
    """Class for representing an account."""

    TYPE_BRAND = "BRAND"
    TYPE_USER = "USER"

    def __init__(self, account_id, account_type, name, email_address, phone_number):
        self.account_id = account_id
        self.account_type = account_type
        self.name = name
        self.email_address = email_address
        self.phone_number = phone_number


class AccountsService:
    """Class for representing connections to the Accounts microservice.

    This is stubbed out for now as the Accounts service doesn't actually exist.
    """

    ACCOUNTS = [
        Account("1ec1e6bc-7906-4859-8edc-eddf6185ced8", Account.TYPE_BRAND, "Test Brand",
                "test@testbrand.com", "+00 12 3456 789"),
        Account("c1d415ed-0d22-4fed-8235-c76e9d69be17", Account.TYPE_USER, "Test User",
                "testuser@gmail.com", "+00 98 7654 321"),
    ]

    @classmethod
    def get_account_by_id(cls, account_id):
        """Return the information for the account with the given account_id."""
        for account in cls.ACCOUNTS:
            if account.account_id == account_id:
                return account
        raise AccountNotFoundError(f"No account could be found with account_id '{account_id}'.")


class AccountNotFoundError(ValueError):
    """Exception for use when an account with the request information could not be found."""
