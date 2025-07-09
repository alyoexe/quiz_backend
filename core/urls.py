from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PDFUploadView, TestView, GenerateQuizView, QuizViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)

urlpatterns = [
    path('upload-pdf/', PDFUploadView.as_view(), name='upload-pdf'),
    path('test/', TestView.as_view(), name='test'),
    path('generate-quiz/<int:pdf_id>/', GenerateQuizView.as_view(), name='generate-quiz'),
]

# Add API URLs from the router
urlpatterns += router.urls
