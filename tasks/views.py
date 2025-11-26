from django.shortcuts import render, redirect, get_object_or_404
from todo import settings
from .models import Task
from .forms import TaskForm


def index(request):
    """Affiche la liste des tâches et permet l'ajout."""

    tasks = Task.objects.all()
    form = TaskForm()

    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('/')

    context = {
        'tasks': tasks,
        'form': form,
        'version': settings.VERSION,
    }
    return render(request, 'tasks/list.html', context)


def updateTask(request, pk):
    """Met à jour une tâche existante."""

    task = get_object_or_404(Task, id=pk)
    form = TaskForm(instance=task)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('/')

    context = {'form': form}
    return render(request, 'tasks/update_task.html', context)


def deleteTask(request, pk):
    """Supprime une tâche après confirmation."""

    item = get_object_or_404(Task, id=pk)

    if request.method == "POST":
        item.delete()
        return redirect('/')

    context = {'item': item}
    return render(request, 'tasks/delete.html', context)
