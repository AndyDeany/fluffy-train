"""Module containing code for representing and handling discount codes."""

import random


class DiscountCode:
    """Class for representing a discount code and its interactions."""

    ALLOWED_CHARACTERS = "ABCDEFGHJKMNPQRTUVWXY346789"  # Exclude characters that look similar
    CODE_LENGTH = 12

    def __init__(self, brand_id):
        """Create and save a discount code with the given brand_id."""
        self.code = self.generate_unique_random_code(self.CODE_LENGTH)
        self.brand_id = brand_id
        self.user_id = None

    @classmethod
    def generate_unique_random_code(cls, length):
        """Generate a unique human readable alphanumeric code."""
        # Collisions are incredibly unlikely (1 in 27^12=1.5x10^17), not worth checking.
        return "".join(random.choice(cls.ALLOWED_CHARACTERS) for _ in range(length))


class CodesDataStore:
    """Class representing a data store for discount codes."""

    codes = []

    @classmethod
    def add_discount_code(cls, discount_code: DiscountCode):
        """Add the given discount_code to the data store."""
        cls.codes.append(discount_code)


class DiscountCodesDataStore(CodesDataStore):
    """Class representing the data store for unallocated generated discount codes."""

    @classmethod
    def allocate_discount_code_from_brand(cls, brand_id, user_id):
        """Allocate a discount code from given brand to the given user and return it.

        The discount code is removed from the list of available discount codes."""
        for code in cls.codes:
            if code.brand_id == brand_id:
                cls.codes.remove(code)
                code.user_id = user_id
                return code
        raise DiscountCodeNotFound(f"No discount code could be found with brand_id '{brand_id}'.")


class UserCodesDataStore(CodesDataStore):
    """Class representing the data store for discount codes that have be allocated to a user."""

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
