from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions,viewsets

from .models import UploadedPDF,Quiz, Question, Option
from .serializers import UploadedPDFSerializer,QuizDetailSerializer
from .utils import extract_text_from_pdf,generate_mcqs_from_text

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
    

class GenerateQuizView(APIView):
    def post(self, request, pdf_id):
        try:
            pdf = UploadedPDF.objects.get(id=pdf_id)
        except UploadedPDF.DoesNotExist:
            return Response({"error": "PDF not found"}, status=404)

        questions = generate_mcqs_from_text(pdf.extracted_text, num_questions=5)

        quiz = Quiz.objects.create(pdf=pdf, title=f"Quiz from {pdf.title}")

        for q in questions:
            ques = Question.objects.create(quiz=quiz, text=q["question"])
            for key, value in q["options"].items():
                Option.objects.create(
                    question=ques,
                    text=value,
                    is_correct=(key == q["answer"])
                )

        return Response({"quiz_id": quiz.id, "message": "Quiz generated successfully"})
    
class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides `list` and `retrieve` endpoints for quizzes.
    """
    queryset = Quiz.objects.all().order_by('-created_at')
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.AllowAny] 