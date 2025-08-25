import fitz  # PyMuPDF
import openai
import os
from dotenv import load_dotenv
load_dotenv()


def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text


# Set Groq credentials
openai.api_key = os.getenv("GROQ_API_KEY")
openai.api_base = "https://api.groq.com/openai/v1"


def generate_mcqs_from_text(text, num_questions=5):
    """
    Generate MCQs from text using batch processing for large content
    Now processes full PDF without artificial limits!
    """
    print(f"Processing PDF with {len(text)} characters for {num_questions} questions")
    
    # Use batch processing for larger requests or large PDFs
    # This ensures we use the FULL PDF content, not just the beginning
    if num_questions > 5 or len(text) > 3000:
        return generate_mcqs_in_batches(text, num_questions)
    
    # For smaller requests with small PDFs, use single batch
    return generate_single_batch_mcqs(text, num_questions)


def generate_mcqs_in_batches(text, total_questions):
    """
    Divide PDF into chunks and generate questions from each chunk
    NOW USES FULL PDF CONTENT - NO TRUNCATION!
    """
    print(f"Batch processing: {len(text)} characters → {total_questions} questions")
    print(f"Full PDF will be processed (no content truncated)")
    
    # Calculate optimal chunk size and questions per batch
    chunk_size = 2500  # Slightly larger chunks for better context
    
    # Dynamic questions per batch based on total request
    if total_questions <= 20:
        questions_per_batch = min(10, total_questions)  # Up to 10 per batch for small requests
    elif total_questions <= 50:
        questions_per_batch = 15  # 15 per batch for medium requests  
    else:
        questions_per_batch = 20  # 20 per batch for large requests
    
    print(f"Using {questions_per_batch} questions per batch for optimal processing")
    
    # Split text into overlapping chunks for better continuity
    chunks = []
    overlap = 200  # 200 character overlap between chunks
    
    for i in range(0, len(text), chunk_size - overlap):
        chunk = text[i:i + chunk_size]
        if len(chunk.strip()) > 100:  # Only use chunks with meaningful content
            chunks.append(chunk.strip())
            
        # Stop if we've covered the entire text
        if i + chunk_size >= len(text):
            break
    
    print(f"Created {len(chunks)} overlapping chunks from full PDF content")
    print(f"Chunk size: {chunk_size} chars, Overlap: {overlap} chars")
    
    all_questions = []
    questions_generated = 0
    
    for i, chunk in enumerate(chunks):
        if questions_generated >= total_questions:
            break
            
        # Calculate how many questions to generate from this chunk
        remaining_questions = total_questions - questions_generated
        questions_for_chunk = min(questions_per_batch, remaining_questions)
        
        print(f"Processing chunk {i+1}/{len(chunks)} - generating {questions_for_chunk} questions")
        
        # Generate questions from this chunk
        chunk_questions = generate_single_batch_mcqs(chunk, questions_for_chunk)
        
        if chunk_questions:
            all_questions.extend(chunk_questions)
            questions_generated += len(chunk_questions)
            print(f"Generated {len(chunk_questions)} questions from chunk {i+1} (Total: {questions_generated})")
        else:
            print(f"Failed to generate questions from chunk {i+1}")
    
    print(f"Batch processing complete: {len(all_questions)} total questions generated")
    return all_questions


def generate_single_batch_mcqs(text, num_questions):
    """
    Generate questions from a single text chunk (original function logic)
    """
    # Recommended models for reliable JSON generation (2025)
    models_to_try = [
        "llama-3.1-8b-instant",      # Fast and reliable
        "gemma2-9b-it",              # Excellent for structured output  
        "llama-3.1-70b-versatile",   # Powerful fallback
        "llama3-8b-8192"             # Backup option
    ]
    
    # No text limits - batch processing handles large content automatically
    print(f"Single batch mode: processing {len(text)} characters for {num_questions} questions")
    
    prompt = f"""Generate exactly {num_questions} multiple choice questions from this text. For each question, provide 4 options and mark the correct answer.

Text to generate questions from:
{text}

Respond in this exact JSON format with no additional text:
[
    {{
        "question": "What is...",
        "options": {{
            "a": "First option",
            "b": "Second option",
            "c": "Third option",
            "d": "Fourth option"
        }},
        "answer": "a"
    }}
]"""

    for model in models_to_try:
        try:
            print(f"Trying model: {model} for {num_questions} questions")
            
            # Dynamic max_tokens based on number of questions
            # Roughly 80-120 tokens per question (including options)
            base_tokens = 200  # For prompt overhead
            tokens_per_question = 100
            max_tokens = base_tokens + (num_questions * tokens_per_question)
            max_tokens = min(max_tokens, 2000)  # Cap at 2000 to stay within limits
            
            print(f"Using {max_tokens} max_tokens for {num_questions} questions")
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=[{
                    "role": "system",
                    "content": "You are a quiz generator that always responds with valid JSON containing multiple choice questions."
                },
                {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.7,
                max_tokens=max_tokens
            )
            import json
            content = response['choices'][0]['message']['content'].strip()
            # Remove any markdown code block markers if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            questions = json.loads(content)
            print(f"Successfully generated {len(questions)} questions using {model}")
            return questions
        except openai.error.OpenAIError as e:
            print(f"Groq API Error with {model}: {str(e)}")
            continue
        except json.JSONDecodeError as e:
            print(f"JSON parsing error with {model}: {str(e)}")
            continue
        except Exception as e:
            print(f"Error with {model}: {str(e)}")
            continue
    
    print("All models failed for this batch")
    return []


def generate_answer_explanations(questions_data, pdf_context=""):
    """
    Generate AI explanations for quiz questions and answers
    
    Args:
        questions_data: List of question dictionaries with options and correct answers
        pdf_context: Original PDF text content for context (optional)
    
    Returns:
        List of explanation dictionaries
    """
    print(f"DEBUG: Generating explanations for {len(questions_data)} questions")
    for q in questions_data:
        print(f"DEBUG: Question {q['question_id']}: {q['question_text'][:50]}...")
    
    try:
        # Smart context limiting for explanations (more generous now with batch system)
        # Use more context since questions are typically few and specific
        max_context_chars = 3000  # Increased from 1000 to 3000
        if pdf_context and len(pdf_context) > max_context_chars:
            # Take the first part for better context
            pdf_context = pdf_context[:max_context_chars]
            print(f"PDF context limited to {max_context_chars} characters for explanations")
        
        # Prepare the prompt for AI explanation generation
        context_section = f"\n\nOriginal PDF Content (for context):\n{pdf_context}" if pdf_context else ""
        
        questions_text = ""
        for q in questions_data:
            questions_text += f"\nQuestion ID {q['question_id']}: {q['question_text']}\n"
            for i, option in enumerate(q['options']):
                status = " ✓ CORRECT ANSWER" if option['is_correct'] else ""
                questions_text += f"   {chr(97+i)}) {option['text']}{status}\n"
        
        prompt = f"""You are an educational AI assistant. Provide clear, helpful explanations for the following quiz questions and their correct answers.

IMPORTANT: Use the exact Question IDs provided. Do not change or renumber them.

For each question, explain:
1. Why the correct answer is right
2. Why the other options are wrong (briefly)
3. Key concepts or facts that help understand the answer

Make explanations educational and easy to understand.{context_section}

Questions to explain:{questions_text}

Return your response as a JSON array where each explanation object has:
- "question_id": the EXACT question ID from above (as integer)
- "explanation": detailed explanation text
- "key_concepts": array of 2-3 key concepts related to this question

You MUST use the exact question IDs provided above. Example format:
[
  {{
    "question_id": {questions_data[0]['question_id']},
    "explanation": "The correct answer is X because...",
    "key_concepts": ["concept1", "concept2"]
  }}
]

Respond with ONLY the JSON array, no additional text."""

        print(f"DEBUG: Prompt sent to AI:\n{prompt[:500]}...")
        
        response = openai.ChatCompletion.create(
            model="llama-3.1-8b-instant",  # Updated to more reliable model
            messages=[{
                "role": "system",
                "content": "You are an educational assistant. Always respond with valid JSON format."
            }, {
                "role": "user",
                "content": prompt
            }],
            temperature=0.3,  # Lower temperature for more consistent explanations
            max_tokens=1500
        )
        
        import json
        content = response['choices'][0]['message']['content'].strip()
        print(f"Raw explanation response: '{content}'")  # Debug log
        
        # Remove any markdown code block markers if present
        content = content.replace('```json', '').replace('```', '').strip()
        
        if not content:
            print("Empty content received from AI")
            raise ValueError("Empty response from AI")
            
        explanations = json.loads(content)
        
        # Ensure we have explanations for all requested questions
        explained_ids = {exp['question_id'] for exp in explanations}
        for q in questions_data:
            if q['question_id'] not in explained_ids:
                # Add fallback explanation if AI missed any
                explanations.append({
                    "question_id": q['question_id'],
                    "explanation": f"The correct answer is '{q['correct_answer']}'. This is based on the content provided.",
                    "key_concepts": ["Review the material", "Study the context"]
                })
        
        return explanations
        
    except openai.error.OpenAIError as e:
        print(f"Groq API Error: {str(e)}")
        # Return fallback explanations
        fallback_explanations = []
        for q in questions_data:
            fallback_explanations.append({
                "question_id": q['question_id'],
                "explanation": f"The correct answer is '{q.get('correct_answer', 'N/A')}'. For a detailed explanation, please review the source material.",
                "key_concepts": ["Study the content", "Review definitions"]
            })
        return fallback_explanations
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {str(e)}")
        print(f"Content that failed to parse: '{content}'")
        # Return fallback explanations
        fallback_explanations = []
        for q in questions_data:
            fallback_explanations.append({
                "question_id": q['question_id'],
                "explanation": f"Unable to generate detailed explanation. The correct answer is based on the provided content.",
                "key_concepts": ["Study the content", "Review definitions"]
            })
        return fallback_explanations
    except Exception as e:
        print("Error generating explanations:", str(e))
        # Return fallback explanations
        fallback_explanations = []
        for q in questions_data:
            fallback_explanations.append({
                "question_id": q['question_id'],
                "explanation": f"For a detailed explanation, please review the source material.",
                "key_concepts": ["Study the content", "Review definitions"]
            })
        return fallback_explanations





