# Quiz Backend

An AI-powered Django REST API that turns uploaded PDF files into interactive multiple-choice quizzes.

Live Demo: [Open the app](https://quizfrontenddepoly.vercel.app/login)

## Features

- Upload PDF files and extract text automatically.
- Generate quizzes with AI from the uploaded content.
- Take quizzes, submit answers, and get instant scores.
- User registration, login, and token-based authentication.
- Quiz history and basic analytics for tracking performance.
- Public or private PDF visibility support.

## Screenshots

![Dashboard](quiz%20screenshot/dashboard.png)
![Uploading PDF](quiz%20screenshot/uploadingpdf.png)
![Quiz Explanation](quiz%20screenshot/explaning.png)
![During Quiz](quiz%20screenshot/duringquiz.png)

## Tech Stack

- Django
- Django REST Framework
- Groq AI
- SQLite / PostgreSQL
- PyMuPDF for PDF text extraction

## Deployment

- Frontend: Vercel
- Backend: Render
- Database: Render PostgreSQL
- Live demo: [Open the app](https://quizfrontenddepoly.vercel.app/login)

## Quick Start

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Main API Flow

1. Upload a PDF.
2. Generate a quiz from the extracted text.
3. View the quiz and answer the questions.
4. Submit answers and receive the score.
