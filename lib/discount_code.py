"""Module containing code for representing and handling discount codes."""

import random
import json


class DiscountCode:
    """Class for representing a discount code and its interactions."""

    ALLOWED_CHARACTERS = "ABCDEFGHJKMNPQRTUVWXY346789"  # Exclude characters that look similar
    CODE_LENGTH = 12

    def __init__(self, brand_id):
        """Create and save a discount code with the given brand_id."""
        self.code = self.generate_unique_random_code(self.CODE_LENGTH)
        self.brand_id = brand_id
        self.user_id = None

    def __eq__(self, other):
        return (self.code == other.code and
                self.brand_id == other.brand_id and self.user_id == other.user_id)

    @classmethod
    def generate_unique_random_code(cls, length):
        """Generate a unique human readable alphanumeric code."""
        # Collisions are incredibly unlikely (1 in 27^12=1.5x10^17), not worth checking.
        return "".join(random.choice(cls.ALLOWED_CHARACTERS) for _ in range(length))

    def to_json(self):
        """Return a json serialized version of the discount code."""
        return {"code": self.code, "brand_id": self.brand_id, "user_id": self.user_id}

    @classmethod
    def from_json(cls, json_code):
        """Create and return a DiscountCode object from the given json."""
        discount_code = DiscountCode(json_code["brand_id"])
        discount_code.code = json_code["code"]
        discount_code.user_id = json_code["user_id"]
        return discount_code


class CodesDataStore:
    """Class representing a data store for discount codes."""

    codes = []
    JSON_FILE = None

    @classmethod
    def add_discount_code(cls, discount_code: DiscountCode):
        """Add the given discount_code to the data store."""
        cls.codes.append(discount_code)
        cls.write_to_json()

    @classmethod
    def remove_discount_code(cls, discount_code: DiscountCode):
        """Remove the given discount_code from the data store."""
        cls.codes.remove(discount_code)
        cls.write_to_json()

    @classmethod
    def write_to_json(cls):
        """Write the contents of the data store to its json file."""
        with open(cls.JSON_FILE, "w") as json_file:
            json.dump([code.to_json() for code in cls.codes], json_file)

    @classmethod
    def read_from_json(cls):
        """Read the contents of the data store from its json file."""
        with open(cls.JSON_FILE, "r") as json_file:
            cls.codes = [DiscountCode.from_json(json_code) for json_code in json.load(json_file)]


class DiscountCodesDataStore(CodesDataStore):
    """Class representing the data store for unallocated generated discount codes."""

    JSON_FILE = "data/discount_codes.json"

    @classmethod
    def allocate_discount_code(cls, brand_id, user_id):
        """Allocate a discount code from given brand to the given user and return it.

        The discount code is removed from the list of available discount codes
        """
        for code in cls.codes:
            if code.brand_id == brand_id:
                cls.remove_discount_code(code)
                code.user_id = user_id
                return code
        raise DiscountCodeNotFound(f"No discount code could be found with brand_id '{brand_id}'.")


class UserCodesDataStore(CodesDataStore):
    """Class representing the data store for discount codes that have be allocated to a user."""

    JSON_FILE = "data/user_codes.json"

    @classmethod
    def find_code(cls, user_id, brand_id):
        """Find and return a discount code for given user+brand combo, if it exists."""
        for code in cls.codes:
            if code.user_id == user_id and code.brand_id == brand_id:
                return code
        raise DiscountCodeNotFound(f"No discount code allocated to user with id '{user_id}' "
                                   f"from brand with id '{brand_id}' could be found.")


class DiscountCodeNotFound(ValueError):
    """Exception for use when a discount code matching the given criteria cannot be found."""


DiscountCodesDataStore.read_from_json()
UserCodesDataStore.read_from_json()
