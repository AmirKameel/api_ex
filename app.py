from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
import fitz  # PyMuPDF

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

# Function to extract TOC and scan for sections not in TOC
def extract_toc_and_sections(pdf_path, expand_pages=7):
    doc = fitz.open(pdf_path)
    toc = doc.get_toc()  # Extract the Table of Contents (TOC)
    sections = {}

    # Create a dictionary to map TOC entries to text in the PDF
    for toc_entry in toc:
        level, title, page = toc_entry
        try:
            # Extract text from the starting page and the following pages
            section_text = ""
            for i in range(page - 1, min(page - 1 + expand_pages + 1, len(doc))):
                page_text = doc.load_page(i).get_text("text")
                if not page_text:
                    page_text = doc.load_page(i).get_text("blocks")  # Try blocks if text is empty
                section_text += page_text if page_text else "Text not available for this section\n"

            # Check if the title already exists in sections, if so append to the list
            if title in sections:
                sections[title].append({
                    "level": level,
                    "page": page,
                    #"text": section_text.strip()
                })
            else:
                sections[title] = [{
                    "level": level,
                    "page": page,
                    #"text": section_text.strip()
                }]
        except Exception as e:
            if title in sections:
                sections[title].append({
                    "level": level,
                    "page": page,
                    #"text": f"Error extracting text: {str(e)}"
                })
            else:
                sections[title] = [{
                    "level": level,
                    "page": page,
                    #"text": f"Error extracting text: {str(e)}"
                }]
    return {"toc": toc, "sections": sections}

class ParsePDF(Resource):

    def post(self):
        """
        Extract TOC and sections from a PDF file.
        ---
        tags:
        - PDF Processing
        parameters:
            - name: pdf
              in: formData
              type: file
              required: true
              description: The PDF file to be processed
            - name: expand_pages
              in: formData
              type: integer
              required: false
              default: 7
              description: Number of pages to expand for each TOC entry
        responses:
            200:
                description: A successful POST request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            toc:
                                type: array
                                description: The Table of Contents (TOC)
                                items:
                                    type: array
                                    items:
                                        type: string
                            sections:
                                type: object
                                description: Extracted sections mapped by TOC title
        """
        if 'pdf' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        pdf_file = request.files['pdf']
        expand_pages = int(request.form.get('expand_pages', 7))

        # Save the PDF temporarily
        pdf_path = f"./temp_{pdf_file.filename}"
        pdf_file.save(pdf_path)

        try:
            result = extract_toc_and_sections(pdf_path, expand_pages=expand_pages)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            import os
            os.remove(pdf_path)  # Clean up the temporary file

        return jsonify(result)

api.add_resource(ParsePDF, "/parse-pdf")

if __name__ == "__main__":
    app.run(debug=True)
