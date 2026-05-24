from docx import Document
import PyPDF2


def extract_text(uploaded_file, filename):

    text = ""
    filename = filename.lower()

    try:

        # TXT FILES
        if filename.endswith('.txt'):
            text = uploaded_file.read().decode(
                'utf-8',
                errors='ignore'
            )

        # DOCX FILES
        elif filename.endswith('.docx'):

            document = Document(uploaded_file)

            paragraphs = []

            for para in document.paragraphs:
                if para.text.strip():
                    paragraphs.append(para.text)

            text = ' '.join(paragraphs)

        # PDF FILES
        elif filename.endswith('.pdf'):

            reader = PyPDF2.PdfReader(uploaded_file)

            pages = []

            for page in reader.pages:

                extracted = page.extract_text()

                if extracted:
                    pages.append(extracted)

            text = ' '.join(pages)

    except Exception as e:
        print("TEXT EXTRACTION ERROR:", e)

    return text.strip()