import typing
import json
import warnings

import requests_ratelimiter

import constants

# Ignore warnings to be printed.
warnings.filterwarnings("ignore")


def _get_data_dict_for_firebase_url(
    encrypted_encoded_coupon_code: str,
) -> dict:
    """
    Depending on the `bool`ean set for `IS_USING_GOOGLE_SHORT_LINK_DEV_API` in `constants` module, this function returns
    proper data to be passed as a `dict` object.

    If the value for `IS_USING_GOOGLE_SHORT_LINK_DEV_API` is set to `True`, then the Dev subscription data is returned.
    Otherwise, the Prod subscription data is returned.

    Args:

    `encrypted_encoded_coupon_code` - The encrypted encoded coupon code in `str`ing format.
    """

    # If `IS_USING_GOOGLE_SHORT_LINK_DEV_API` is set to `True`, return data related to Dev subscription.
    if constants.IS_USING_GOOGLE_SHORT_LINK_DEV_API:
        print("[-] Returning data for DEV subscription...")

        # TODO: Edit below data dictionary for Dev subscription.
        return {
            "dynamicLinkInfo": {
                "domainUriPrefix": "DOMAIN_URI_PREFIX_URL",
                "link": f"https://LINK_TO_BE_SHORTENED/{encrypted_encoded_coupon_code}",
                "androidInfo": {"androidPackageName": "ANDROID_PACKAGE_NAME"},
                "iosInfo": {"iosBundleId": "IOS_PACKAGE_NAME"},
            }
        }

    # Otherwise return data related to Prod subscription.
    print("[-] Returning data for PROD subscription...")

    # TODO: Edit below data dictionary for Prod subscription.
    return {
        "dynamicLinkInfo": {
            "domainUriPrefix": "DOMAIN_URI_PREFIX_URL",
            "link": f"https://LINK_TO_BE_SHORTENED/{encrypted_encoded_coupon_code}",
            "androidInfo": {"androidPackageName": "ANDROID_PACKAGE_NAME"},
            "iosInfo": {"iosBundleId": "IOS_PACKAGE_NAME"},
        }
    }


def collect_firebase_short_urls(
    encrypted_encoded_coupon_codes_list: typing.List[str],
    unique_ids_to_short_url_dict: dict,
) -> None:
    """
    Fetches the Firebase short URLs using pre-defined `rate_limiter_session`.

    Args:

    `encrypted_encoded_coupon_codes_list` - This is list of Unique ID strings in encrypted and encoded format.
    `unique_ids_to_short_url_dict` - This is a mapping to store Unique ID with created short URLs. This will be useful to check which short URL is mapped against which encrypted encoded Unique ID.
    """
    headers_dict: dict = {
        "Content-Type": "application/json",
    }

    params_dict: dict = {
        "key": "CUSTOM_KEY",  # TODO: Use appropriate key.
    }

    firebase_url: str = "CUSTOM_FIREBASE_ENDPOINT"  # TODO: Use appropriate endpoint.

    # A `LimiterSession` that will be used to control the POST requests per second.
    rate_limited_session: requests_ratelimiter.LimiterSession = (
        requests_ratelimiter.LimiterSession(
            per_second=constants.GOOGLE_API_REQUESTS_PER_SECOND,
        )
    )

    # Iterate over all of encrypted encoded codes to get and store short URLs.
    for encrypted_encoded_coupon_code in encrypted_encoded_coupon_codes_list:
        # Prepare the data to pass in POST request.
        data_dict: dict = _get_data_dict_for_firebase_url(
            encrypted_encoded_coupon_code=encrypted_encoded_coupon_code,
        )

        try:
            # Send POST request using rate limited session.
            response_obj: requests_ratelimiter.Response = rate_limited_session.post(
                url=firebase_url,
                params=params_dict,
                headers=headers_dict,
                data=json.dumps(data_dict),
                timeout=60.0,  # https://stackoverflow.com/a/56941261
                verify=False,  # https://stackoverflow.com/a/51768580
            )

            response_dict: dict = json.loads(response_obj.text)

            if "shortLink" in response_dict:
                unique_ids_to_short_url_dict[
                    encrypted_encoded_coupon_code
                ] = response_dict["shortLink"]
            else:
                unique_ids_to_short_url_dict[encrypted_encoded_coupon_code] = ""
                print(
                    f"[!] Short link not received for: {encrypted_encoded_coupon_code}"
                )

            print(f"- URLs mapped : {len(unique_ids_to_short_url_dict.keys())}")

        except Exception as ex:
            if encrypted_encoded_coupon_code not in unique_ids_to_short_url_dict:
                unique_ids_to_short_url_dict[encrypted_encoded_coupon_code] = ""

            print(
                "\n (!) Unable to get url for {} due to {}.".format(
                    encrypted_encoded_coupon_code, ex.__class__
                )
            )
            print(f"[!] URLs mapped : {len(unique_ids_to_short_url_dict.keys())}")
