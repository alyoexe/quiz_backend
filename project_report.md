Great! Let me explain the complete quiz backend project we've built so far, including all the features and how they work together.

## **Project Overview: AI-Powered Quiz Backend**

This is a Django REST API that allows users to upload PDF documents and automatically generate multiple-choice quizzes using AI (Groq LLM). Here's the complete breakdown:

## **Core Features Built:**

### **1. PDF Upload & Text Extraction**
**Endpoint:** `POST /api/upload-pdf/`

```python
# What happens:
1. User uploads a PDF file
2. System extracts text using PyMuPDF (fitz)
3. Stores PDF metadata and extracted text in database
4. Returns PDF ID for next steps
```

**Models involved:**
- `UploadedPDF`: Stores file, title, user, extracted text

### **2. AI Quiz Generation**
**Endpoint:** `POST /api/generate-quiz/{pdf_id}/`

```python
# What happens:
1. Takes PDF ID from upload step
2. Gets extracted text from database
3. Sends text to Groq AI (Mixtral model) with structured prompt
4. AI generates 5 multiple choice questions with 4 options each
5. Stores questions and options in database
6. Returns quiz ID
```

**Models involved:**
- `Quiz`: Links to PDF, stores title and creation time
- `Question`: Stores question text, links to quiz
- `Option`: Stores answer options, marks which is correct

### **3. Quiz Retrieval**
**Endpoints:**
- `GET /api/quizzes/` - List all quizzes
- `GET /api/quizzes/{quiz_id}/` - Get specific quiz with all questions & options

```python
# What you get:
{
  "id": 1,
  "title": "Quiz from Deep Sea PDF",
  "created_at": "2025-08-23T07:55:43Z",
  "questions": [
    {
      "id": 1,
      "text": "What is the deepest part of the ocean?",
      "options": [
        {"id": 1, "text": "Mariana Trench", "is_correct": true},
        {"id": 2, "text": "Atlantic Ridge", "is_correct": false}
      ]
    }
  ]
}
```

### **4. Quiz Submission & Scoring**
**Endpoint:** `POST /api/submit-quiz/{quiz_id}/`

```python
# User sends:
{
  "answers": [
    {"question_id": 1, "option_id": 3},
    {"question_id": 2, "option_id": 7}
  ]
}

# System returns:
{
  "score": 3,
  "total_questions": 5,
  "percentage": 60.0,
  "results": [...] // Detailed breakdown
}
```

**Models involved:**
- `QuizAttempt`: Records who took quiz, when, and final score
- `UserAnswer`: Records each individual answer for detailed analysis

## **Authentication System Added:**

### **5. User Registration & Login**
**Endpoints:**
- `POST /api/register/` - Create new user account
- `POST /api/login/` - Login and get auth token

```python
# Registration:
POST /api/register/
{
  "username": "john_doe",
  "email": "john@email.com", 
  "password": "securepass123"
}

# Response:
{
  "user_id": 1,
  "username": "john_doe",
  "token": "abc123token456"
}

# Login:
POST /api/login/
{
  "username": "john_doe",
  "password": "securepass123"  
}
```

**How Authentication Works:**
- Uses Django's built-in User model
- Token-based authentication (each user gets a unique token)
- Token must be included in headers for protected endpoints: `Authorization: Token abc123token456`

### **6. User History & Analytics**

**User Quiz History:**
`GET /api/user/quiz-history/`
```python
# Shows all quizzes user has taken:
{
  "attempts": [
    {
      "attempt_id": 1,
      "quiz_title": "Deep Sea Quiz",
      "score": 4,
      "total_questions": 5,
      "percentage": 80.0,
      "submitted_at": "2025-08-23T15:30:00Z"
    }
  ]
}
```

**Quiz Analytics:**
`GET /api/quiz/{quiz_id}/analytics/`
```python
# Shows statistics for a specific quiz:
{
  "quiz_title": "Deep Sea Quiz",
  "total_attempts": 25,
  "average_score": 3.2,
  "average_percentage": 64.0,
  "pass_rate": 72.0,
  "highest_score": 5,
  "lowest_score": 1
}
```

## **Database Structure:**

```
Users (Django built-in)
├── UploadedPDF (user's PDF files)
    ├── Quiz (generated from PDF)
        ├── Question (multiple per quiz)
            └── Option (4 per question, one marked correct)
        └── QuizAttempt (user's attempt record)
            └── UserAnswer (individual answers)
```

## **Technology Stack:**

- **Backend:** Django + Django REST Framework
- **Database:** SQLite (can be changed to PostgreSQL)
- **AI:** Groq API (Mixtral-8x7b model)
- **File Processing:** PyMuPDF for PDF text extraction
- **Authentication:** Token-based auth
- **Environment:** Python with dotenv for API keys

## **Current API Endpoints Summary:**

```
# Core Functionality:
POST /api/upload-pdf/           # Upload PDF
POST /api/generate-quiz/{id}/   # Generate quiz from PDF
GET  /api/quizzes/             # List all quizzes  
GET  /api/quizzes/{id}/        # Get specific quiz
POST /api/submit-quiz/{id}/    # Submit answers & get score

# User Management:
POST /api/register/            # Create account
POST /api/login/              # Login

# Analytics:
GET /api/user/quiz-history/    # User's attempt history
GET /api/quiz/{id}/analytics/  # Quiz performance stats

# Utility:
GET /api/test/                # Test endpoint
```

## **Workflow Example:**

1. **User registers:** `POST /api/register/`
2. **User uploads PDF:** `POST /api/upload-pdf/` → gets PDF ID
3. **Generate quiz:** `POST /api/generate-quiz/7/` → gets Quiz ID  
4. **View quiz:** `GET /api/quizzes/14/` → see questions & options
5. **Take quiz:** `POST /api/submit-quiz/14/` → get score & results
6. **Check history:** `GET /api/user/quiz-history/` → see all attempts

This creates a complete learning management system where users can transform any PDF document into an interactive quiz powered by AI!