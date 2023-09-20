from django.shortcuts import render
from rest_framework.views import APIView
from .serlializers import ProjectSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import Project , Image , Sound
from .google_drive import *
from django.contrib.auth.models import User
# Create your views here.

class CreateProject(APIView):
    def get(self , request , *args , **kwargs):
        pass
    def post(self , request , *args , **kwargs):
        print(request.data)
        # Access the projectName from request.POST
        #project_name = request.POST.get('projectName')

        # Access the uploaded files from request.FILES
        #images = request.FILES.getlist('image')
        #audios = request.FILES.getlist('audio')
        
        #print(project_name)
        #print(images)
        #print(audios)
        serializer = ProjectSerializer(data = request.data)
        if serializer.is_valid():
                project_name = serializer.validated_data['projectName']
                images = serializer.validated_data['image']
                audios = serializer.validated_data['audio']
                #print(project_name)
                #print(image)
                #print(audio)
                #print(serializer.data)
                author = User.objects.get(username = 'admin')
                project = Project.objects.create(author = author , name = project_name)
                user_folder_id = get_user_folder_id(author.username)
                project_folder_id = create_folder(user_folder_id , project_name)
                
                for image in images:
                    image_id = upload_file_to_google_drive(image , image.name , project_folder_id)
                    Image.objects.create(project = project , image_name = image.name)
                for audio in audios: 
                    sound_id = upload_file_to_google_drive(audio , audio.name , project_folder_id)
                    Sound.objects.create(project = project , sound_name = audio.name)
                return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
    