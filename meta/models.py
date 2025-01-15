from django.db import models
from django_ckeditor_5.fields import CKEditor5Field

# Create your models here.
class About(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='about/')
    
    def __str__(self):
        return self.title
    
class WhoWeAre(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='about/')
    
    def __str__(self):
        return self.title
    
class Philosophy(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='about/')
    
    def __str__(self):
        return self.title
    

class FAQ(models.Model):
    question = models.CharField(max_length=100)
    answer = models.TextField()
    
    def __str__(self):
        return self.question

  
class PrivacyPolicy(models.Model):
    title = models.CharField(max_length=100,null=True, blank=True)
    description = CKEditor5Field('Text', config_name='extends', null=True, blank=True)
    
    def __str__(self):
        return self.title


class TermsAndCondition(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    
    def __str__(self):
        return self.title