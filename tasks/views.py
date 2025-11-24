from django.shortcuts import render, redirect
# from django.http import HttpResponse  # Import inutile, supprimé pour éviter F401

from todo import settings
from .models import Task  # Import explicite du modèle Task
from .forms import TaskForm  # Import explicite du formulaire TaskForm

# Vue principale affichant la liste des tâches et le formulaire d'ajout
def index(request):
    # Récupère toutes les tâches de la base de données
    tasks = Task.objects.all()

    # Instancie un formulaire vide pour ajouter une nouvelle tâche
    form = TaskForm()

    if request.method == 'POST':
        # Si le formulaire est soumis, on le remplit avec les données POST
        form = TaskForm(request.POST)
        if form.is_valid():
            # Si le formulaire est valide, on sauvegarde la nouvelle tâche
            form.save()
        # Redirection vers la page principale après ajout
        return redirect('/')

    # Contexte pour le template : tâches, formulaire et version de l'application
    context = {
        'tasks': tasks,
        'form': form,
        'version': settings.VERSION
    }
    return render(request, 'tasks/list.html', context)


# Vue pour mettre à jour une tâche existante
def updateTask(request, pk):
    # Récupère la tâche à modifier par son id
    task = Task.objects.get(id=pk)
    # Instancie le formulaire avec les données de la tâche existante
    form = TaskForm(instance=task)

    if request.method == "POST":
        # Remplit le formulaire avec les nouvelles données POST
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            # Sauvegarde les modifications si le formulaire est valide
            form.save()
            return redirect('/')

    # Contexte pour le template : formulaire pré-rempli
    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)


# Vue pour supprimer une tâche
def deleteTask(request, pk):
    # Récupère la tâche à supprimer par son id
    item = Task.objects.get(id=pk)

    if request.method == "POST":
        # Supprime l'objet et redirige vers la page principale
        item.delete()
        return redirect('/')

    # Contexte pour le template : tâche à confirmer pour suppression
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)
