from django.contrib import admin
#Importation du modele Task
from .models import Task  

# Register your models here.
admin.site.register(Task)
