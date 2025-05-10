import boto3
import uuid
import time
from datetime import datetime
from PyPDF2 import PdfReader
from docx import Document

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

# DynamoDB Tables
resumes_table = dynamodb.Table('Resumes')
interactions_table = dynamodb.Table('ResumeInteractions')

def lambda_handler(event, context):
    route = event['routeKey']
    
    if route == 'POST /upload':
        return handle_upload(event)
    elif route == 'GET /interactions/{resumeId}':
        return handle_get_interactions(event)
    else:
        return {'statusCode': 404, 'body': 'Not Found'}

def handle_upload(event):
    # Get file from API Gateway
    file_content = base64.b64decode(event['body'])
    file_name = event['headers']['filename']
    user_id = event['headers']['user-id']  # From Cognito in real implementation
    
    # Generate unique ID
    resume_id = str(uuid.uuid4())
    
    # Upload to S3
    s3.put_object(
        Bucket='resume-tracking-bucket',
        Key=f'resumes/{resume_id}',
        Body=file_content
    )
    
    # Parse resume
    parsed_data = parse_resume(file_content, file_name)
    
    # Store metadata
    resumes_table.put_item(Item={
        'resumeId': resume_id,
        'userId': user_id,
        'fileName': file_name,
        'uploadDate': datetime.now().isoformat(),
        **parsed_data
    })
    
    return {
        'statusCode': 200,
        'body': {'resumeId': resume_id}
    }

def parse_resume(file_content, file_name):
    # Basic parsing example
    text = ""
    if file_name.endswith('.pdf'):
        pdf = PdfReader(file_content)
        text = " ".join([page.extract_text() for page in pdf.pages])
    elif file_name.endswith('.docx'):
        doc = Document(file_content)
        text = " ".join([para.text for para in doc.paragraphs])
    
    return {
        'skills': extract_skills(text),
        'experience': extract_experience(text),
        'education': extract_education(text)
    }

def handle_get_interactions(event):
    resume_id = event['pathParameters']['resumeId']
    
    response = interactions_table.query(
        KeyConditionExpression='resumeId = :rid',
        ExpressionAttributeValues={':rid': resume_id}
    )
    
    return {
        'statusCode': 200,
        'body': response['Items']
    }

# Tracking Middleware (to be called on resume access)
def track_interaction(resume_id, action='view'):
    interactions_table.put_item(Item={
        'interactionId': str(uuid.uuid4()),
        'resumeId': resume_id,
        'timestamp': datetime.now().isoformat(),
        'action': action,
        'viewerInfo': get_viewer_info()  # Implement based on auth system
    })

# Helper functions (implement according to needs)
def extract_skills(text): ...
def extract_experience(text): ...
def extract_education(text): ...
def get_viewer_info(): ...
