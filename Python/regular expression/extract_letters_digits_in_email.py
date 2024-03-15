"""
    Using regular expression, it can extract letter and digits present in the email address.

    It removes everything after `@` character and also ignore all special characters like `.`, `-`, `+`, or `_`.
"""

import re

user_email: str = "Samp_le.2-5@email.com"

pattern: re.Pattern = re.compile(r"[\W_]+", re.UNICODE)
letters_digits_str: str = pattern.sub("", user_email.split("@")[0])
print(f"Original Email: {user_email}")
print(f"Extracted: {letters_digits_str}")
