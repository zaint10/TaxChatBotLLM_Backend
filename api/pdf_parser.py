import re
import os
from django.core.files.storage import default_storage
from pdf2image import convert_from_path
from llms import openai_client


def parse_pdf(pdf_file):
    try:
        # Convert PDF to images
        images = convert_pdf_to_images(pdf_file)
        
        # Extract text from images using OpenAI vision models
        extracted_text = extract_text_from_images(images)

        # Parse extracted text to get W-2 data
        # w2_data = parse_extracted_text(extracted_text)
        
        return extracted_text
    except Exception as e:
        raise e

def convert_pdf_to_images(pdf_file):
    # Convert PDF pages to images using pdf2image library
    images = convert_from_path(pdf_file)
    return images

def extract_text_from_images(images):
    client = openai_client.ChatHandler()
    extracted_text = client.ocr(images)
    
    return extracted_text

def parse_extracted_text(extracted_text):
    # Initialize dictionary to store extracted data
    extracted_data = {}

    # Remove markdown formatting characters
    extracted_text = re.sub(r'[*#-]', '', extracted_text)

    # Extract data using regular expressions
    employee_ssn_match = re.search(r"Employee.* Social Security Number:\s*(.*)", extracted_text, re.IGNORECASE)
    if employee_ssn_match:
        extracted_data['employee_ssn'] = employee_ssn_match.group(1)

    employee_name_match = re.search(r"Employee.* Name:\s*(.*)", extracted_text, re.IGNORECASE)
    if employee_name_match:
        extracted_data['employee_name'] = employee_name_match.group(1)
    
    employee_address_match = re.search(r"Employee.* Address:\s*(.*)", extracted_text, re.IGNORECASE)
    if employee_address_match:
        extracted_data['employee_address'] = employee_address_match.group(1)

    employer_name_match = re.search(r"Employer.* Name:\s*(.*)", extracted_text, re.IGNORECASE)
    if employer_name_match:
        extracted_data['employer_name'] = employer_name_match.group(1)

    employer_address_match = re.search(r"Employer.* Address:\s*(.*)", extracted_text, re.IGNORECASE)
    if employer_address_match:
        extracted_data['employer_address'] = employer_address_match.group(1)

    employer_ein_match = re.search(r"EIN.*:\s*([\d-]+)", extracted_text, re.IGNORECASE)
    if employer_ein_match:
        extracted_data['employer_ein'] = employer_ein_match.group(1)

    employer_sin_match = re.search(r"Employer.* State ID Number:\s*(.*)", extracted_text, re.IGNORECASE)
    if employer_sin_match:
        extracted_data['employer_sin'] = employer_sin_match.group(1)

    total_compensation_match = re.search(r"Wages, Tips, Other Compensation:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if total_compensation_match:
        extracted_data['total_compensation'] = total_compensation_match.group(1)

    social_security_wages_match = re.search(r"Social Security Wages:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if social_security_wages_match:
        extracted_data['social_security_wages'] = social_security_wages_match.group(1)

    social_security_tax_withheld_match = re.search(r"Social Security Tax.*:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if social_security_tax_withheld_match:
        extracted_data['social_security_tax_withheld'] = social_security_tax_withheld_match.group(1)

    medicare_wages_match = re.search(r"Medicare Wages and Tips:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if medicare_wages_match:
        extracted_data['medicare_wages'] = medicare_wages_match.group(1)

    medicare_tax_withheld_match = re.search(r"Medicare Tax.*:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if medicare_tax_withheld_match:
        extracted_data['medicare_tax_withheld'] = medicare_tax_withheld_match.group(1)

    federal_income_tax_withheld_match = re.search(r"Federal Income Tax.*:\s*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if federal_income_tax_withheld_match:
        extracted_data['federal_income_tax_withheld'] = federal_income_tax_withheld_match.group(1)

    state_wages_match = re.search(r"State Wages.*:\s*[\w\s]*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if state_wages_match:
        extracted_data['state_wages'] = state_wages_match.group(1)

    state_income_tax_withheld_match = re.search(r"State Income Tax.*:\s*[\w\s]*([$]?[\d,]+\.\d{2})", extracted_text, re.IGNORECASE)
    if state_income_tax_withheld_match:
        extracted_data['state_income_tax'] = state_income_tax_withheld_match.group(1)

    control_number_match = re.search(r"Control Number:\s*(.*)", extracted_text, re.IGNORECASE)
    if control_number_match:
        extracted_data['control_number'] = control_number_match.group(1)

    return extracted_data

def save_uploaded_file(pdf_file, username):
    # Define directory path to store files
    USER_W2_UPLOADS_DIR = os.environ.get('USER_W2_UPLOADS_DIR')
    user_directory = os.path.join(USER_W2_UPLOADS_DIR, username)
    os.makedirs(user_directory, exist_ok=True)

    # Save the uploaded PDF file to disk
    file_path = os.path.join(user_directory, pdf_file.name)
    with default_storage.open(file_path, 'wb+') as destination:
        for chunk in pdf_file.chunks():
            destination.write(chunk)

    return file_path
