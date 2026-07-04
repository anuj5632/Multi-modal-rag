import fitz
import os

IMAGE_DIR = "extracted_images"

os.makedirs(IMAGE_DIR, exist_ok = True)

def extract_images(pdf_path, document_id=None):
    """
    document_id: if provided, filenames are namespaced as
    "{document_id}_page_{n}_image_{i}.ext" to avoid collisions between
    different PDFs that happen to have images on the same page number.
    Falls back to the old naming if document_id isn't passed, for
    backwards compatibility with any existing callers.
    """

    document = fitz.open(pdf_path)

    extracted_images = []

    prefix = f"{document_id}_" if document_id else ""

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        images = page.get_images(full = True)

        for image_index, image in enumerate(images):

            xref = image[0]

            image_data = document.extract_image(xref)

            image_bytes = image_data["image"]

            extension = image_data["ext"]

            filename = (
                f"{prefix}page_{page_number+1}"
                f"_image_{image_index+1}.{extension}"
            )

            image_path = os.path.join(
                IMAGE_DIR, filename
            )

            with open(image_path, "wb") as img:
                img.write(image_bytes)

            extracted_images.append(
                {
                    "page" : page_number + 1,
                    "image_path" : image_path
                }
            )

    document.close()
    return extracted_images
