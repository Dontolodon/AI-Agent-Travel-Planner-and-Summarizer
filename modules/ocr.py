import pytesseract
from PIL import Image, ImageOps

def extract_image_text(image_path: str) -> str:
    img = Image.open(image_path)
    img = ImageOps.grayscale(img)

    w, h = img.size
    img = img.resize((w * 2, h * 2))

    img = ImageOps.autocontrast(img)
    img = img.point(lambda x: 0 if x < 160 else 255, "1")

    config = "--oem 1 --psm 6"
    return pytesseract.image_to_string(img, config=config)
