# https://github.com/lincolnloop/python-qrcode

import os

import qrcode

from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
)

from qrcode.image.styles.colormasks import RadialGradiantColorMask

qr: qrcode.QRCode = qrcode.QRCode(
    border=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
)
qr.add_data("URL_TO_ADD_IN_QR_CODE")  # TODO: Mention URL to encode in QR code.


# Type of patterns to generate.
module_drawer_list: list = [
    SquareModuleDrawer,
    GappedSquareModuleDrawer,
    CircleModuleDrawer,
    RoundedModuleDrawer,
    VerticalBarsDrawer,
    HorizontalBarsDrawer,
]

idx: int = 0

for cls_idx, module_drawer in enumerate(module_drawer_list):
    img = qr.make_image(
        embeded_image_path=os.path.join(
            "PATH_TO", "IMAGE_TO_EMBED.PNG"
        ),  # TODO: Edit image path.
        image_factory=StyledPilImage,
        module_drawer=module_drawer(),
        color_mask=RadialGradiantColorMask(
            center_color=(0, 64, 221),
            edge_color=(215, 0, 21),
        ),
    )
    img_path: str = os.path.join(
        "PATH_TO_OUTPUT", f"{idx}.png"
    )  # TODO: Edit image path.

    img.save(img_path)

    print(f"- Written image: {idx}.png")
    idx += 1
