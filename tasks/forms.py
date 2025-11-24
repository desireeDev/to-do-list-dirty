from django import forms
# On a supprimé 'from django.forms import ModelForm' car il n'était pas utilisé
from .models import Task  # On importe explicitement seulement le modèle Task

class TaskForm(forms.ModelForm):
    # Champ personnalisé avec un placeholder
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Ajouter une nouvelle tâche'})
    )

    class Meta:
        model = Task  # On indique explicitement que ce formulaire correspond au modèle Task
        fields = '__all__'  # On inclut tous les champs du modèle dans le formulaire
