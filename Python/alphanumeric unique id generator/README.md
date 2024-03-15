## Alphanumeric Unique ID Generator

Repository contains full source code for application that can generate alpha-numeric unique IDs and encrypt them. Then it can fetch the short link using Google Firebase API and store everything in CSV/Excel files.
When generating unique IDs from web application UI, it spawns a separate background process, which is independent from the web app server process.

Below are the details for each of the source code file:

1. **`constants.py`** :

    Contains definitions for various constants to be used across the application. This have definitions for numeric values, file or directory paths, application name, host address, port number and so on. It also has variable to easily enable or disable the application's execution in debug mode.

    Also, if the debug mode is enabled, then we'll have different paths which mostly relate to local development setup. If it's disabled, then those paths mostly relate to production server environment.

2. **`encryptor_encoder.py`** :

    Constains the function definition that can encrypt (using [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem)) algorithm), encode (using URL-safe [Base64](https://en.wikipedia.org/wiki/Base64) encoding) and return a string.

    This will be used to generate encrypted, encoded string representation for coupon code/unique ID passed as function parameter. To perform the RSA encryption, this function will refer (or generate new if not exist) the required key file.

3. **`firebase_url_shortner.py`** :

    Contains the function definition that takes in the encrypted, encoded list of coupon codes and can fetch the short URL link for each of those using Google API in a rate limited way. Finally, it returns a mapping of those coupon codes with short URLs as a `dict`ionary object.

    In free tier, the Google API has restriction of _5 requests per second_. So, this is handled here to prevent any of quota expiry issues.

4. **`utility_functions.py`** : 

    Contains some of the most commonly used function definitions required by different modules of the application.

    Its functions will handle the default data values and formats required by some application controls, managing internal tracking of how many records have been generated (by avoiding data race conditions), reading last or writing new alpha-numeric unique ID length, and computing remaining quota for the day etc.

5. **`uid_generator.py`** :

    Contains full implementation logic to generate the sequence of coupon codes/unique IDs.

    It manages to continue process from where the last coupon code generated, generating the new codes/IDs, calling necessary functions from other modules to track the generation process, short URL generation, referring last alpha-numeric unique ID length or write new length for it, and writing the actual result file in the end.

6. **`dash_instance.py`** :

    Contains the user interface controls definitions which will be called when application link is opened in the browser.

    It also maintains the shared objects and ensures these will be created only once throughout the application lifecycle.

7. **`dash_callback.py`** :

    Contains the callback function definitions which will be triggered when user interacts with any of UI controls.

    This handles the input validation, starting the coupon codes/unique IDs generation in a separate process if all inputs are valid.

8. **`app.py`** :

    The entry point of the application from where the execution will be started.
    
    After installing all the dependencies from [`requirements.txt`](./requirements.txt) file, this is the file which should be run using command: _`python3 app.py`_
