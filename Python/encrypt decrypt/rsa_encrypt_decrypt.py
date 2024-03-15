import base64
import os
import rsa

unique_ids: list = ["AB00000000001", "CD00000000002", "EF00000000003"]

public_key: rsa.PublicKey = None
private_key: rsa.PrivateKey = None

if not os.path.exists("public_key.pem") and not os.path.exists("private_key.pem"):
    public_key, private_key = rsa.newkeys(256)
    with open("public_key.pem", "wb") as public_file:
        public_file.write(public_key.save_pkcs1())
    with open("private_key.pem", "wb") as private_file:
        private_file.write(private_key.save_pkcs1())
else:
    with open("public_key.pem", "rb") as public_file:
        public_key = rsa.PublicKey.load_pkcs1(public_file.read())
    with open("private_key.pem", "rb") as private_file:
        private_key = rsa.PrivateKey.load_pkcs1(private_file.read())

for idx, data in enumerate(unique_ids):
    enc_message: bytes = rsa.encrypt(data.encode(), public_key)
    print(f"\n{idx + 1})\n- original = {data}")
    print(
        f"- encrypted ({len(enc_message.hex())}) = {enc_message}\n{enc_message.hex()}"
    )

    base64_encoded: bytes = base64.urlsafe_b64encode(enc_message)
    print(f"- base64 encoded ({len(base64_encoded)}) = {base64_encoded}")

    base64_decoded: bytes = base64.urlsafe_b64decode(base64_encoded)
    print(f"- base64 decoded ({len(base64_decoded)}) = {base64_decoded}")

    # dec_message = rsa.decrypt(enc_message, private_key).decode()
    dec_message = rsa.decrypt(base64_decoded, private_key).decode()
    print(f"- decrypted = {dec_message}")
