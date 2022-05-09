"""Module containing the main API."""

import traceback

from flask import Flask
from flask_restful import Api
from werkzeug.exceptions import HTTPException

from lib.generate_codes import GenerateCodes


app = Flask(__name__)


@app.errorhandler(404)
def not_found(_error):
    """Handle all uncaught 404s from incorrect URLs."""
    return {"message": "The URL could not be found."}, 404


class EnhancedApi(Api):
    """Class enhancing the basic flask_restful.Api class."""

    def handle_error(self, e):
        """Handle errors thrown by API calls."""
        if isinstance(e, HTTPException):
            return super().handle_error(e)  # Handle abort() calls normally
        # And catch other thrown Exceptions to give a custom 500 payload.
        print(traceback.format_exc())
        return {"message": "There was an Internal Server Error. Oh no."}, 500


if __name__ == "__main__":
    api = EnhancedApi(app)
    api.add_resource(GenerateCodes, "/generate-codes")
    app.run(debug=True)
