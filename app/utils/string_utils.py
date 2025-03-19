import base64
import random
import re
import string
from urllib.parse import urlparse


class StringUtils:
    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choice(characters) for _ in range(length))
        return random_string

    @staticmethod
    def clean_string(input_string: str) -> str:
        # Remove non-ASCII characters
        cleaned_string = re.sub(r"[^\x00-\x7F]+", " ", input_string)

        # Consolidate spaces and ensure correct spacing around punctuation
        cleaned_string = re.sub(r"\s*([.,;!?%:])\s*", r"\1 ", cleaned_string)

        # Adjust spacing for the dollar sign
        cleaned_string = re.sub(r"\$\s+", "$", cleaned_string)

        # Ensure correct spacing inside parentheses around numbers
        cleaned_string = re.sub(r"\(\s*(\d+)\s*\)", r"( \1 )", cleaned_string)

        # Remove extra spaces around punctuation (this might be redundant but ensures
        # no trailing space before punctuation)
        cleaned_string = re.sub(r"\s+([.,;!?%:])", r"\1", cleaned_string)

        # Remove leading and trailing whitespace, reduce multiple spaces to a single
        # space, and convert to lower case
        cleaned_string = re.sub(r"\s+", " ", cleaned_string).strip().lower()

        return cleaned_string

    @staticmethod
    def get_file_name_without_extension(file_name: str) -> str:
        return ".".join(file_name.split(".")[:-1])

    @staticmethod
    def is_valid_url(url: str):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def is_base64(string: str) -> bool:
        """
        Validates if the input string is a Base64-encoded string.

        Args:
            string (str): The string to validate.

        Returns:
            bool: True if the string is Base64, False otherwise.
        """
        try:
            # Check if the string can be decoded
            base64_bytes = base64.b64decode(string, validate=True)
            # Check if decoded bytes can be re-encoded to the original string
            return base64.b64encode(base64_bytes).decode("utf-8") == string
        except Exception:
            return False
