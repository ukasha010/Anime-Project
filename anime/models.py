from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Project(models.Model):
    author = models.ForeignKey(User , on_delete=models.CASCADE)
    name = models.TextField()
    
    def __str__(self):
        return self.name
    
class Image(models.Model):
    project = models.ForeignKey(Project , on_delete=models.CASCADE)
    image_name = models.TextField()
    
    def __str__(self):
        return f'{self.project} image'
    
class Sound(models.Model):
    project = models.ForeignKey(Project , on_delete=models.CASCADE)
    sound_name = models.TextField()
    
    def __str__(self):
        return f'{self.project} sound'