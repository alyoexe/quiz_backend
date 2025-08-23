from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PDFUploadView, TestView, GenerateQuizView, QuizViewSet, 
    SubmitQuizView, UserQuizHistoryView, QuizAnalyticsView
)
from .authentication import RegisterView, LoginView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'quizzes', QuizViewSet)

urlpatterns = [
    # PDF and Quiz Management
    path('upload-pdf/', PDFUploadView.as_view(), name='upload-pdf'),
    path('generate-quiz/<int:pdf_id>/', GenerateQuizView.as_view(), name='generate-quiz'),
    path('submit-quiz/<int:quiz_id>/', SubmitQuizView.as_view(), name='submit-quiz'),
    
    # User Management
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # Analytics and History
    path('user/quiz-history/', UserQuizHistoryView.as_view(), name='user-quiz-history'),
    path('quiz/<int:quiz_id>/analytics/', QuizAnalyticsView.as_view(), name='quiz-analytics'),
    
    # Test endpoint
    path('test/', TestView.as_view(), name='test'),
]

# Add API URLs from the router
urlpatterns += router.urls
