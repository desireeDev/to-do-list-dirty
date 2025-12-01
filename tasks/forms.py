from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """Formulaire pour le modèle Task."""
    
    title = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'placeholder': 'Ajouter une nouvelle tâche',
                'class': 'form-control',
                'id': 'id_title'
            }
        ),
        label="Titre de la tâche"
    )
    
    # NOUVEAUX CHAMPS
    priority = forms.BooleanField(
        required=False,
        label="Tâche prioritaire ⚡",
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_priority'
        })
    )

    class Meta:
        model = Task
        fields = ['title', 'complete', 'priority']  # AJOUTER 'priority'