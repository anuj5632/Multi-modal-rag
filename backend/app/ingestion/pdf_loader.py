import fitz

def extract_text_from_pdf(pdf_path:str):
    document = fitz.open(pdf_path)

    pages = []

    for page_number in range(len(document)):
        page = document.load_page(page_number)

        text = page.get_text()

        pages.append(
            {
                "page" : page_number + 1,
                "text" : text
            }
        )

    document.close()

    return pages    