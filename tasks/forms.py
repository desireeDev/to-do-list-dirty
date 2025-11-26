from django import forms
from .models import Task


class TaskForm(forms.ModelForm):
    """Formulaire pour le modèle Task avec un placeholder."""

    title = forms.CharField(
        widget=forms.TextInput(
            attrs={'placeholder': 'Ajouter une nouvelle tâche'}
        )
    )

    class Meta:
        model = Task
        fields = '__all__'
