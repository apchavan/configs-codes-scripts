import base64
import os

import rsa

import constants


def encrypt_encode_unique_id(
    unique_id_str: str,
) -> str:
    """
    Returns encrypted and URL-safe Base64 encoded representation of `unique_id_str` in string format.
    """

    # Create a sub-directory where all public and private secret key files are stored.
    secret_keys_dir_name: str = constants.SECRET_KEYS_DIR_PATH
    os.makedirs(name=secret_keys_dir_name, exist_ok=True)

    # Create file names for public and private key files.
    public_encryptor_file_path: str = os.path.join(
        secret_keys_dir_name, f"public_encryptor.pem"
    )
    private_decryptor_file_path: str = os.path.join(
        secret_keys_dir_name, f"private_decryptor.pem"
    )

    public_key: rsa.PublicKey = None
    private_key: rsa.PrivateKey = None

    if not os.path.exists(public_encryptor_file_path) or not os.path.exists(
        private_decryptor_file_path
    ):
        # If any one of keys not found, then generate and store new keys.
        public_key, private_key = rsa.newkeys(256)

        with open(public_encryptor_file_path, "wb") as public_file:
            public_file.write(public_key.save_pkcs1())

        with open(private_decryptor_file_path, "wb") as private_file:
            private_file.write(private_key.save_pkcs1())

    else:
        # Otherwise, read key data from existing files.
        with open(public_encryptor_file_path, "rb") as public_file:
            public_key = rsa.PublicKey.load_pkcs1(public_file.read())

        with open(private_decryptor_file_path, "rb") as private_file:
            private_key = rsa.PrivateKey.load_pkcs1(private_file.read())

    encrypted_message: bytes = rsa.encrypt(unique_id_str.encode(), public_key)
    base64_encoded: bytes = base64.urlsafe_b64encode(encrypted_message)

    return base64_encoded.decode()
