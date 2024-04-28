import os
import openai

from utils import encode_image
class ChatHandler:
    def __init__(self, api_key=os.environ.get('OPENAI_API_KEY')):
        self.api_key = api_key
        self.openai = openai.OpenAI()
        self.openai.api_key = api_key

    def chat(self, messages):
        try:
            response = self.openai.chat.completions.create(
                model='gpt-4',
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            # Handle any errors or exceptions
            return f"Error occurred: {str(e)}"
    
    def ocr(self, images):
        extracted_text = ""
        for image in images:

            # Getting the base64 string
            base64_image = encode_image(image)
            # Use OpenAI's vision models to extract text from the images
            prompt = '''
            Extract key data from the W-2 form, including:
            1. Employee information (Employee's Social Security Number, Employee's name, Employer's name, Employee's address, Employer's address, EIN and Employer's state ID number).
            2. Salary details (wages, tips, compensation, medicare wages, social security, State wages).
            3. Tax withholdings (federal income tax, social security tax, Medicare tax, state income tax, and control number).
            if value doesn't exists, must leave it empty. Please accurately extract data.
            '''
            response = self.openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", "text": prompt
                                },
                            {
                                "type": "image_url",
                                "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ],
                max_tokens=350,
            )
            extracted_text += response.choices[0].message.content + " "
            
        return extracted_text
