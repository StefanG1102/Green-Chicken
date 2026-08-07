import os

import cv2


def save_analysis_image(image, file_path):
    """
    Speichert das Analysebild als PNG oder JPG.

    :param image:
        OpenCV-Bild als NumPy-Array.

    :param file_path:
        Zielpfad, z. B.
        /Users/name/Desktop/analyse.png
    """

    if image is None:
        raise ValueError(
            "Es ist kein Analysebild vorhanden."
        )

    if not file_path:
        raise ValueError(
            "Kein Speicherpfad angegeben."
        )

    extension = os.path.splitext(
        file_path
    )[1].lower()

    if extension not in (
        ".png",
        ".jpg",
        ".jpeg",
    ):
        raise ValueError(
            "Unterstützte Bildformate: PNG und JPG."
        )

    success = cv2.imwrite(
        file_path,
        image
    )

    if not success:
        raise IOError(
            "Das Analysebild konnte nicht gespeichert werden."
        )

    return True