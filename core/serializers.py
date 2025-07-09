from rest_framework import serializers
from .models import UploadedPDF,Quiz, Question, Option

class UploadedPDFSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedPDF
        fields = '__all__'
        read_only_fields = ['user', 'uploaded_at', 'extracted_text']

class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ['id', 'text', 'is_correct']

class QuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, source='option_set')

    class Meta:
        model = Question
        fields = ['id', 'text', 'options']

class QuizDetailSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, source='question_set')

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'created_at', 'questions']