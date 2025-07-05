from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions

from .models import UploadedPDF
from .serializers import UploadedPDFSerializer
from .utils import extract_text_from_pdf

class PDFUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    #permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get('pdf_file')
        title = request.data.get('title', 'Untitled')

        if not file:
            return Response({'error': 'No file provided'}, status=400)

        # Handle case when user is not authenticated
        user = request.user if request.user.is_authenticated else None

        pdf_instance = UploadedPDF.objects.create(
            user=user,
            title=title,
            pdf_file=file
        )

        # Extract text
        text = extract_text_from_pdf(pdf_instance.pdf_file.path)
        pdf_instance.extracted_text = text
        pdf_instance.save()

        serializer = UploadedPDFSerializer(pdf_instance)
        return Response(serializer.data, status=201)

class TestView(APIView):
    def get(self, request):
        return Response({"message": "Test endpoint working"}, status=status.HTTP_200_OK)
