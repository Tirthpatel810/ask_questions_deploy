from django.shortcuts import render

import requests
from .models import Question
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from django.shortcuts import render
import requests
from .models import Question
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .translate import translate
from django.http import JsonResponse
import json

from reportlab.lib.pagesizes import letter
from io import BytesIO
from django.core.mail import EmailMessage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.graphics.shapes import Drawing, Line

import pyttsx3

def index(request):
    return render(request, 'index.html')

@api_view(['POST'])
def get_reddit_answers(request):
    question_text = request.data.get('question', '')

    if not question_text:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        question = Question.objects.get(question_text=question_text, source='reddit')
        return Response({'question': question_text, 'answers': question.answers}, status=status.HTTP_200_OK)
    except Question.DoesNotExist:
        url = f"https://www.reddit.com/search.json?q={question_text}&sort=relevance&t=all"
        headers = {'User-Agent': 'Q&A_app/0.1 by TirthPatel0810'}

        try:
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                reddit_data = response.json()
                if 'data' not in reddit_data or 'children' not in reddit_data['data']:
                    return Response({'error': 'No relevant data found'}, status=status.HTTP_204_NO_CONTENT)

                results = []
                for post in reddit_data['data']['children']:
                    title = post['data'].get('title', 'No title available')
                    permalink = post['data'].get('permalink', '')
                    description = post['data'].get('selftext', '')
                    url = f"https://www.reddit.com{permalink}"
                    
                    results.append({
                        'title': title,
                        'description': description,
                        'url': url
                    })

                Question.objects.create(question_text=question_text, source='reddit', answers=results)

                return Response({'question': question_text, 'answers': results}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch from Reddit'}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def get_stackoverflow_answers(request):
    question_text = request.data.get('question', '')

    if not question_text:
        return Response({'error': 'No question provided'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        question = Question.objects.get(question_text=question_text, source='stackoverflow')
        return Response({'question': question_text, 'answers': question.answers}, status=status.HTTP_200_OK)
    except Question.DoesNotExist:
        url = "https://api.stackexchange.com/2.3/search/advanced"
        params = {
            'order': 'desc',
            'sort': 'relevance',
            'q': question_text,
            'site': 'stackoverflow'
        }

        try:
            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                stackoverflow_data = response.json()

                if 'items' not in stackoverflow_data or not stackoverflow_data['items']:
                    return Response({'error': 'No relevant data found'}, status=status.HTTP_204_NO_CONTENT)

                results = []
                for post in stackoverflow_data['items']:
                    title = post.get('title', 'No title available')
                    link = post.get('link', '')
                    tags = post.get('tags', [])
                    answer_count = post.get('answer_count', 0)

                    results.append({
                        'title': title,
                        'link': link,
                        'tags': tags,
                        'answer_count': answer_count
                    })

                Question.objects.create(question_text=question_text, source='stackoverflow', answers=results)
                return Response({'question': question_text, 'answers': results}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Failed to fetch from Stack Overflow'}, status=response.status_code)

        except requests.exceptions.RequestException as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def translate_question(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question', [])
            language = data.get('language', 'english')

            if not isinstance(question, list):
                question = [question]

            translated_question = ''
            for q in question:
                if isinstance(q, (int, float)):
                    translated_part = str(q)
                else:
                    translated_part = translate(q, language)
                
                if translated_part:
                    translated_question += translated_part + ' '
                else:
                    pass

            return JsonResponse({'translated_question': translated_question.strip()})
        except (ValueError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def generate_pdf(answers):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    title_style = styles['Title']
    title_style.textColor = colors.darkblue
    title_style.leading = 24
    title_style.fontSize = 16

    section_style = ParagraphStyle('SectionStyle', parent=styles['Heading2'], textColor=colors.black)
    section_style.leading = 14
    
    description_style = ParagraphStyle('DescriptionStyle', parent=styles['BodyText'], textColor=colors.black)
    description_style.leading = 14
    description_style.backColor = colors.whitesmoke
    description_style.fontSize = 12
    
    content = []
    content.append(Paragraph("StackOverflow/Reddit Answers Report", title_style))

    for answer in answers:
        section_content = []
        section_content.append(Paragraph(f"<b>Title:</b> {answer.get('title', 'No title available')}", section_style))
        try:
            description = answer.get('description')
            if description == '':
                description = 'No description available'
            else:
                if len(description) > 300:
                    description = description[:300] + '...'
            section_content.append(Paragraph(f"<b>Description:</b><br/>{description}", description_style))
        except:
            tags = answer.get('tags', [])
            section_content.append(Paragraph(f"<b>Tags:</b> {', '.join(tags) if tags else 'Not available'}", description_style))

            answer_count = answer.get('answer_count', 'Not available')
            section_content.append(Paragraph(f"<b>Answer Count:</b> {answer_count}", description_style))
        
        url = answer.get('url') or answer.get('link')
        if url and not url.startswith(('http://', 'https://')):
            url = None
        if url:
            section_content.append(Paragraph(f"<b>Link:</b> <a href='{url}'>View on Website</a>", description_style))
        else:
            section_content.append(Paragraph("<b>Link:</b> Not available", description_style))

        section_content.append(Paragraph("", description_style))

        for paragraph in section_content:
            content.append(paragraph)
        line = Drawing(400, 1)
        line.add(Line(0, 0, 400, 0))
        content.append(line)
        content.append(Spacer(1, 10))
    
    doc.build(content)
    buffer.seek(0)
    return buffer

def send_report_via_email(answers, recipient_email):
    
    pdf = generate_pdf(answers)
    email = EmailMessage(
        subject="Your StackOverflow or Reddit Answers Report",
        body="Please find the attached report.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )

    email.attach('answers_report.pdf', pdf.read(), 'application/pdf')  
    email.send()
    
    pdf.close()


@csrf_exempt
def generate_report_and_send_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        answers = data.get('answers', [])
        recipient_email = data.get('email')

        send_report_via_email(answers, recipient_email)

        return JsonResponse({"message": "Report sent successfully!"})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
def speak_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text = data.get('text', '')
            if text:
                engine = pyttsx3.init('sapi5')
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[1].id)
                engine.setProperty('rate', 170)

                engine.say(text)
                engine.runAndWait()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'No text provided'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})