"""Module for managing interactions with the Authorization Microservice."""


class AuthorizationService:
    """Class for representing connections to the Authorization microservice.

    This is stubbed out for now as the Authorization service doesn't actually exist.
    """

    BEARER_TOKENS = {   # Fake tokens
        "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9": "1ec1e6bc-7906-4859-8edc-eddf6185ced8",
        "Bearer SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJVQa": "c1d415ed-0d22-4fed-8235-c76e9d69be17",
    }

    @classmethod
    def validate_token(cls, bearer_token):
        """Return the account_id of the account a given bearer token relates to if it is valid.

        Raises InvalidTokenError if the given bearer token is not valid.
        """
        try:
            return cls.BEARER_TOKENS[bearer_token]
        except KeyError:
            raise InvalidTokenError(f"Bearer token '{bearer_token}' is invalid or unauthorized.")


class InvalidTokenError(ValueError):
    """Exception for use when an invalid bearer token is used."""
