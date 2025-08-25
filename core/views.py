from django.shortcuts import render
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status, permissions,viewsets

from .models import UploadedPDF,Quiz, Question, Option, QuizAttempt, UserAnswer
from .serializers import UploadedPDFSerializer,QuizDetailSerializer
from .utils import extract_text_from_pdf,generate_mcqs_from_text, generate_answer_explanations

class PDFUploadView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    #permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        file = request.FILES.get('pdf_file')
        title = request.data.get('title', 'Untitled')
        is_public = request.data.get('is_public', 'true').lower() == 'true'  # Default to public

        if not file:
            return Response({'error': 'No file provided'}, status=400)

        # Handle case when user is not authenticated
        user = request.user if request.user.is_authenticated else None

        pdf_instance = UploadedPDF.objects.create(
            user=user,
            title=title,
            pdf_file=file,
            is_public=is_public
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
    """
    Generate quiz from PDF
    POST /api/generate-quiz/{pdf_id}/
    
    Optional payload:
    {
        "num_questions": 10
    }
    """
    def post(self, request, pdf_id):
        try:
            pdf = UploadedPDF.objects.get(id=pdf_id)
        except UploadedPDF.DoesNotExist:
            return Response({"error": "PDF not found"}, status=404)

        # Get number of questions from request data, default to 5
        num_questions = request.data.get('num_questions', 5)
        
        # Validate num_questions (no upper limit - batch processing handles any amount!)
        if not isinstance(num_questions, int) or num_questions < 1:
            return Response({
                "error": "num_questions must be a positive integer (minimum 1)"
            }, status=400)
        
        # Add reasonable upper limit to prevent abuse (can be adjusted)
        if num_questions > 200:
            return Response({
                "error": "Maximum 200 questions per request (to prevent timeout). Please make multiple requests for more."
            }, status=400)

        questions = generate_mcqs_from_text(pdf.extracted_text, num_questions=num_questions)

        # Check if AI generated any questions
        if not questions:
            return Response({
                "error": "Failed to generate questions. Please try again or use a different PDF."
            }, status=500)

        # Create quiz with actual number of questions generated
        actual_questions_count = len(questions)
        quiz = Quiz.objects.create(
            pdf=pdf, 
            title=f"Quiz from {pdf.title} ({actual_questions_count} questions)"
        )

        for q in questions:
            ques = Question.objects.create(quiz=quiz, text=q["question"])
            for key, value in q["options"].items():
                Option.objects.create(
                    question=ques,
                    text=value,
                    is_correct=(key == q["answer"])
                )

        return Response({
            "quiz_id": quiz.id, 
            "message": f"Quiz with {actual_questions_count} questions generated successfully",
            "requested_questions": num_questions,
            "questions_generated": actual_questions_count
        })
    
class QuizViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides `list` and `retrieve` endpoints for quizzes.
    GET /api/quizzes/ - List all public quizzes + user's private quizzes
    GET /api/quizzes/{id}/ - Get specific quiz (if public or belongs to user)
    """
    queryset = Quiz.objects.all()  # Default queryset (will be overridden by get_queryset)
    serializer_class = QuizDetailSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        user = self.request.user if self.request.user.is_authenticated else None
        
        if user:
            # Show public quizzes + user's own private quizzes
            return Quiz.objects.filter(
                Q(pdf__is_public=True) | Q(pdf__user=user)
            ).order_by('-created_at')
        else:
            # Show only public quizzes for anonymous users
            return Quiz.objects.filter(pdf__is_public=True).order_by('-created_at')
    
    def retrieve(self, request, pk=None):
        try:
            quiz = Quiz.objects.get(pk=pk)
            user = request.user if request.user.is_authenticated else None
            
            # Check if user can access this quiz
            if not quiz.pdf.is_public and quiz.pdf.user != user:
                return Response({"error": "This quiz is private"}, status=403)
            
            serializer = self.get_serializer(quiz)
            return Response(serializer.data)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)


class SubmitQuizView(APIView):
    """
    Submit quiz answers and get score
    POST /api/submit-quiz/{quiz_id}/
    
    Expected payload:
    {
        "answers": [
            {"question_id": 1, "option_id": 3},
            {"question_id": 2, "option_id": 7}
        ]
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)
        
        # Debug: Print the received data
        print("Received data:", request.data)
        
        answers = request.data.get('answers', [])
        if not answers:
            return Response({
                "error": "No answers provided", 
                "received_data": str(request.data)
            }, status=400)
        
        if not isinstance(answers, list):
            return Response({
                "error": "Answers must be a list", 
                "received_type": str(type(answers))
            }, status=400)
        
        user = request.user if request.user.is_authenticated else None
        total_questions = quiz.question_set.count()
        
        # Create quiz attempt
        attempt = QuizAttempt.objects.create(
            quiz=quiz,
            user=user,
            total_questions=total_questions
        )
        
        correct_count = 0
        results = []
        
        for answer_data in answers:
            question_id = answer_data.get('question_id')
            option_id = answer_data.get('option_id')
            
            print(f"Processing: question_id={question_id}, option_id={option_id}")
            
            try:
                question = Question.objects.get(id=question_id, quiz=quiz)
                print(f"Found question: {question.text[:50]}...")
                
                selected_option = Option.objects.get(id=option_id, question=question)
                print(f"Found option: {selected_option.text}")
                
                is_correct = selected_option.is_correct
                if is_correct:
                    correct_count += 1
                
                # Save user answer
                UserAnswer.objects.create(
                    attempt=attempt,
                    question=question,
                    selected_option=selected_option,
                    is_correct=is_correct
                )
                
                # Get correct answer for response
                correct_option = Option.objects.get(question=question, is_correct=True)
                
                results.append({
                    "question_id": question_id,
                    "question_text": question.text,
                    "selected_option": selected_option.text,
                    "correct_option": correct_option.text,
                    "is_correct": is_correct
                })
                
            except Question.DoesNotExist:
                print(f"Question with id={question_id} not found in quiz {quiz_id}")
                return Response({
                    "error": f"Question with id {question_id} not found in this quiz"
                }, status=400)
            except Option.DoesNotExist:
                print(f"Option with id={option_id} not found for question {question_id}")
                return Response({
                    "error": f"Option with id {option_id} not found for question {question_id}"
                }, status=400)
        
        # Update attempt score
        attempt.score = correct_count
        attempt.save()
        
        return Response({
            "attempt_id": attempt.id,
            "score": correct_count,
            "total_questions": total_questions,
            "percentage": round((correct_count / total_questions) * 100, 2),
            "results": results
        })


class UserQuizHistoryView(APIView):
    """
    Get user's quiz attempt history
    GET /api/user/quiz-history/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        
        if not user:
            # For anonymous users, we could track by session or return empty
            return Response({"message": "Login required to view history", "attempts": []})
        
        attempts = QuizAttempt.objects.filter(user=user).select_related('quiz').order_by('-submitted_at')
        
        history = []
        for attempt in attempts:
            history.append({
                "attempt_id": attempt.id,
                "quiz_title": attempt.quiz.title,
                "score": attempt.score,
                "total_questions": attempt.total_questions,
                "percentage": round((attempt.score / attempt.total_questions) * 100, 2),
                "submitted_at": attempt.submitted_at,
            })
        
        return Response({"attempts": history})


class QuizAttemptDetailView(APIView):
    """
    Get detailed information about a specific quiz attempt
    GET /api/attempt/{attempt_id}/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, attempt_id):
        try:
            attempt = QuizAttempt.objects.get(id=attempt_id)
        except QuizAttempt.DoesNotExist:
            return Response({"error": "Quiz attempt not found"}, status=404)
        
        # Get all user answers for this attempt
        user_answers = UserAnswer.objects.filter(attempt=attempt).select_related(
            'question', 'selected_option'
        )
        
        # Build detailed results
        results = []
        for user_answer in user_answers:
            # Get correct answer for this question
            correct_option = Option.objects.get(
                question=user_answer.question, 
                is_correct=True
            )
            
            results.append({
                "question_id": user_answer.question.id,
                "question_text": user_answer.question.text,
                "selected_option": user_answer.selected_option.text,
                "selected_option_id": user_answer.selected_option.id,
                "correct_option": correct_option.text,
                "correct_option_id": correct_option.id,
                "is_correct": user_answer.is_correct
            })
        
        return Response({
            "attempt_id": attempt.id,
            "quiz_title": attempt.quiz.title,
            "quiz_id": attempt.quiz.id,
            "score": attempt.score,
            "total_questions": attempt.total_questions,
            "percentage": round((attempt.score / attempt.total_questions) * 100, 2),
            "submitted_at": attempt.submitted_at,
            "results": results
        })


class QuizAnalyticsView(APIView):
    """
    Get analytics for a specific quiz
    GET /api/quiz/{quiz_id}/analytics/
    """
    permission_classes = [permissions.AllowAny]
    
    def get(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)
        
        attempts = QuizAttempt.objects.filter(quiz=quiz)
        total_attempts = attempts.count()
        total_questions = quiz.question_set.count()
        
        if total_attempts == 0:
            return Response({
                "quiz_title": quiz.title,
                "total_questions": total_questions,
                "total_attempts": 0,
                "average_score": 0,
                "average_percentage": 0.0,
                "pass_rate": 0.0,
                "highest_score": 0,
                "lowest_score": 0
            })
        
        scores = [attempt.score for attempt in attempts]
        average_score = sum(scores) / len(scores)
        average_percentage = (average_score / total_questions) * 100
        
        # Consider 60% as passing threshold
        passing_threshold = 0.6
        passing_score = total_questions * passing_threshold
        passed_attempts = len([score for score in scores if score >= passing_score])
        pass_rate = (passed_attempts / total_attempts) * 100
        
        return Response({
            "quiz_title": quiz.title,
            "total_questions": total_questions,
            "total_attempts": total_attempts,
            "average_score": round(average_score, 1),
            "average_percentage": round(average_percentage, 1),
            "pass_rate": round(pass_rate, 1),
            "passing_threshold": f"{int(passing_threshold * 100)}%",
            "highest_score": max(scores),
            "lowest_score": min(scores)
        })


class QuizExplanationView(APIView):
    """
    Get AI-generated explanations for quiz questions/answers
    POST /api/quiz/{quiz_id}/explain/
    
    Expected payload:
    {
        "question_ids": [1, 2, 3],  # List of question IDs to explain
        "include_context": true      # Whether to include PDF context in explanation (optional, default: true)
    }
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, quiz_id):
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)
        
        # Check if user can access this quiz
        user = request.user if request.user.is_authenticated else None
        if not quiz.pdf.is_public and quiz.pdf.user != user:
            return Response({"error": "This quiz is private"}, status=403)
        
        question_ids = request.data.get('question_ids', [])
        include_context = request.data.get('include_context', True)
        
        if not question_ids:
            return Response({"error": "No question_ids provided"}, status=400)
        
        if not isinstance(question_ids, list):
            return Response({"error": "question_ids must be a list"}, status=400)
        
        # Validate question IDs belong to this quiz
        questions = Question.objects.filter(id__in=question_ids, quiz=quiz).prefetch_related('option_set')
        
        if questions.count() != len(question_ids):
            found_ids = list(questions.values_list('id', flat=True))
            invalid_ids = [qid for qid in question_ids if qid not in found_ids]
            return Response({
                "error": f"Some question IDs don't belong to this quiz: {invalid_ids}"
            }, status=400)
        
        # Prepare questions data for AI explanation
        questions_data = []
        for question in questions:
            options = question.option_set.all()
            correct_option = options.filter(is_correct=True).first()
            
            question_info = {
                "question_id": question.id,
                "question_text": question.text,
                "options": [{"text": opt.text, "is_correct": opt.is_correct} for opt in options],
                "correct_answer": correct_option.text if correct_option else "N/A"
            }
            questions_data.append(question_info)
        
        # Get PDF context if requested
        pdf_context = quiz.pdf.extracted_text if include_context else ""
        
        try:
            # Generate explanations using AI
            explanations = generate_answer_explanations(questions_data, pdf_context)
            
            return Response({
                "quiz_id": quiz.id,
                "quiz_title": quiz.title,
                "explanations": explanations
            })
            
        except Exception as e:
            return Response({
                "error": "Failed to generate explanations",
                "details": str(e)
            }, status=500) 