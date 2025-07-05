from rest_framework import serializers
from .models import UploadedPDF

class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = '__all__'
        read_only_fields = ['user', 'uploaded_at', 'extracted_text']
