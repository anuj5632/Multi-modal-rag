import fitz 
import os

IMAGE_DIR = "extracted_images"

os.makedirs(IMAGE_DIR, exist_ok = True)

def extract_images(pdf_path):

    document = fitz.open(pdf_path)

    extracted_images = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        images = page.get_images(full = True)

        for image_index, image in enumerate(images):

            xref = image[0]

            image_data = document.extract_image(xref)

            image_bytes = image_data["image"]

            extension = image_data["ext"]

            filename = (
                f"page_{page_number+1}"
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