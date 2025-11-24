from django.shortcuts import render, redirect, get_object_or_404
from todo import settings  # Pour accéder à la version de l'application
from .models import Task   # Import du modèle Task
from .forms import TaskForm  # Import du formulaire TaskForm

# -------------------------------------------------------------------
# Vue principale affichant la liste des tâches et permettant l'ajout
# -------------------------------------------------------------------
def index(request):
    # Récupère toutes les tâches de la base
    tasks = Task.objects.all()

    # Instancie un formulaire vide pour l'ajout d'une tâche
    form = TaskForm()

    if request.method == 'POST':
        # Si le formulaire est soumis, le remplir avec les données POST
        form = TaskForm(request.POST)
        if form.is_valid():
            # Sauvegarde la tâche si le formulaire est valide
            form.save()
        # Redirection vers la page principale après ajout
        return redirect('/')

    # Contexte passé au template : liste des tâches, formulaire et version de l'app
    context = {
        'tasks': tasks,
        'form': form,
        'version': settings.VERSION
    }
    return render(request, 'tasks/list.html', context)


# -------------------------------------------------------------------
# Vue pour mettre à jour une tâche existante
# -------------------------------------------------------------------
def updateTask(request, pk):
    # Récupère la tâche par ID ou renvoie une 404 si elle n'existe pas
    task = get_object_or_404(Task, id=pk)

    # Pré-remplit le formulaire avec les données de la tâche existante
    form = TaskForm(instance=task)

    if request.method == "POST":
        # Met à jour la tâche avec les nouvelles données du formulaire
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            # Sauvegarde les modifications
            form.save()
            # Redirection vers la page principale après mise à jour
            return redirect('/')

    # Contexte pour le template : formulaire pré-rempli
    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)


# -------------------------------------------------------------------
# Vue pour supprimer une tâche
# -------------------------------------------------------------------
def deleteTask(request, pk):
    # Récupère la tâche à supprimer ou renvoie une 404 si l'ID est invalide
    item = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        # Supprime la tâche et redirige vers la page principale
        item.delete()
        return redirect('/')

    # Contexte pour le template : tâche à confirmer pour suppression
    context = {'item': item}
    return render(request, 'tasks/delete.html', context)
