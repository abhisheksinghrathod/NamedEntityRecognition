from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .models import PDFDocument
from .serializers import PDFDocumentSerializer
import pdfplumber
import spacy
from spacy.matcher import Matcher

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Initialize Matcher
matcher = Matcher(nlp.vocab)

# Define patterns for common email-like fields
patterns = [
    {"label": "FROM", "pattern": [{"LOWER": "from"}, {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"IS_ALPHA": True, "OP": "+"}]},
    {"label": "TO", "pattern": [{"LOWER": "to"}, {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"IS_ALPHA": True, "OP": "+"}]},
    {"label": "DATE", "pattern": [{"LOWER": "date"}, {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"IS_DIGIT": True, "OP": "+"}]},
    {"label": "SUBJECT", "pattern": [{"LOWER": "subject"}, {"IS_PUNCT": True, "OP": "?"}, {"IS_SPACE": True, "OP": "*"}, {"IS_ALPHA": True, "OP": "+"}]}
]

# Add patterns to matcher
for p in patterns:
    matcher.add(p["label"], [p["pattern"]])

class PDFUploadView(APIView):
    queryset = PDFDocument.objects.all()
    serializer_class = PDFDocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        try:
            file_obj = request.FILES.get('file')
            if file_obj:
                text = ""
                with pdfplumber.open(file_obj) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""

                # Apply NER
                doc = nlp(text)
                entities = [{'text': ent.text, 'label': ent.label_} for ent in doc.ents]

                # Apply rule-based matching
                matches = matcher(doc)
                for match_id, start, end in matches:
                    label = nlp.vocab.strings[match_id]
                    span = doc[start:end]
                    entities.append({'label': label, 'text': span.text})

                serializer = self.serializer_class(data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': "PDF uploaded and processed successfully.",
                        'entities': entities
                    })
                return Response(serializer.errors, status=400)
        except Exception as e:
            print("file upload failed with error:", e)
        return Response({'error': 'No file uploaded'}, status=400)
