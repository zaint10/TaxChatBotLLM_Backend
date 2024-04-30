import json
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from api.pdf_parser import parse_pdf, save_uploaded_file
from api.serializers import PDFUploadSerializer, ChatSerializer, W2FormSerializer
from api.models import W2Form
from llms.openai_client import ChatHandler
# Create your views here.

class W2FormViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = W2Form.objects.all()
    serializer_class = W2FormSerializer
    
class W2FormUpload(APIView):
    serializer_class = PDFUploadSerializer
    
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        uploaded_file = request.FILES['file']
        
        if serializer.is_valid():
            uploaded_file = serializer.validated_data['file']
            file_path = save_uploaded_file(uploaded_file, request.user.username)
            extracted_data = parse_pdf(file_path)
            obj_w2form = W2Form.objects.create(user=request.user, file_name=uploaded_file.name, data=extracted_data)
            
            return Response({
                "message": "W-2 form parsed and saved successfully", 
                "data": {
                    "w2form_id": obj_w2form.id
                    }
                }, status=status.HTTP_201_CREATED
                            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatView(APIView):
    serializer_class = ChatSerializer
    
    def post(self, request, w2form_id):
        # Check if the W-2 form ID exists
        obj_w2form = get_object_or_404(W2Form, pk=w2form_id)
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            question = serializer.validated_data['question']
            messages = json.loads(obj_w2form.messages)
            if not len(messages):
                messages.append({
                    "role": "system", "content": obj_w2form.data
                })
            messages.append({
                "role": "user", "content": question
            })
            openai_client = ChatHandler()
            answer = openai_client.chat(messages)
            messages.append({
                "role": "system", "content": answer
            })
            messages = json.dumps(messages)
            obj_w2form.messages=messages
            obj_w2form.save()
            
            response_data = {'question': question, 'response': answer}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)