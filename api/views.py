from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import pdfplumber
import pytesseract
import cv2
import numpy as np
from PIL import Image
import logging

class PDFOCRView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        manual_rotation = int(request.query_params.get('manual_rotation', 0))
        try:
            if not file_obj:
                return Response({'error': 'No file uploaded'}, status=400)

            text = self.perform_ocr_on_pdf(file_obj, manual_rotation)
            return Response({'message': 'OCR completed successfully.', 'extracted_text': text})
        except Exception as e:
            logging.error(f"Error processing OCR: {str(e)}")
            return Response({'error': 'Failed to process file'}, status=500)

    def perform_ocr_on_pdf(self, pdf_file, manual_rotation):
        """Extract text from a PDF with optional rotation correction and table preservation."""
        try:
            ocr_text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    pil_image = page.to_image(resolution=300).original
                    open_cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
                    gray_image = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)

                    osd = pytesseract.image_to_osd(gray_image, output_type=pytesseract.Output.DICT)
                    angle = osd["rotate"] + manual_rotation

                    if abs(angle) > 1:
                        gray_image = self.rotate_image(gray_image, -angle)

                    table_data = self.extract_table_data(page)
                    if table_data:
                        ocr_text += "---TABLE DETECTED---\n"
                        for row in table_data:
                            ocr_text += " | ".join([str(cell) or "" for cell in row]) + "\n"
                        ocr_text += "---END OF TABLE---\n"

                    processed_pil_image = Image.fromarray(gray_image)
                    ocr_text += pytesseract.image_to_string(processed_pil_image, lang="eng")
            return ocr_text
        except Exception as e:
            logging.error(f"Error during OCR processing: {str(e)}")
            raise

    def rotate_image(self, image, angle):
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

    def extract_table_data(self, page):
        try:
            return page.extract_tables() or None
        except Exception as e:
            logging.error(f"Error extracting tables: {str(e)}")
            return None
