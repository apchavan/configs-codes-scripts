# https://github.com/heuer/segno

import os
import segno
from PIL import Image as PilImage

original_url: str = "URL_TO_ADD_IN_QR_CODE"  # TODO: Mention URL to encode in QR code.

qrcode = segno.make_qr(
    content=original_url,
    error="H",
)
# qrcode.save("qrcode_output.png")
print(qrcode.version)

img: PilImage = qrcode.to_artistic(
    background=os.path.join(
        "PATH_TO", "BACKGROUND_IMAGE.PNG"
    ),  # TODO: Edit image path.
    target=os.path.join("PATH_TO", "TARGET_IMAGE.PNG"),  # TODO: Edit image path.
    kind="png",
    finder_dark="#cc2229",
    # separator="#cc2229",
    alignment_dark="#cc2229",
    # alignment_light="#cc2229",
    data_dark="#4676ce",
    # light="#4676ce",
    dark="#cc2229",
    border=1,
    scale=15,
)
# .convert("RGBA")

# qrcode.save("qrcode_output.png")
