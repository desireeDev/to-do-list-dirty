# tasks/test_priority.py
from django.test import TestCase
from tasks.models import Task
from tasks.forms import TaskForm
from django.urls import reverse
from tasks.decorators import tc 

class TaskPriorityTests(TestCase):
    """Tests TDD pour la fonctionnalité de priorité des tâches."""
    # ============== PHASE RED - Tests qui échouent ==============
    
    @tc("TP001")
    def test_create_task_with_priority_field(self):
        """TP001: Test que le modèle Task a un champ priority."""
        # Ce test doit échouer d'abord (champ n'existe pas encore)
        task = Task(title="Test tâche")
        self.assertTrue(hasattr(task, 'priority'), 
                       "Le modèle Task doit avoir un champ 'priority'")
    
    @tc("TP002")
    def test_priority_default_value_is_false(self):
        """TP002: Test que la priorité est False par défaut."""
        task = Task.objects.create(title="Tâche test")
        self.assertFalse(task.priority,
                        "La priorité doit être False par défaut")
    
    @tc("TP003")
    def test_create_priority_task(self):
        """TP003: Test création d'une tâche prioritaire."""
        task = Task.objects.create(title="Tâche URGENTE", priority=True)
        self.assertTrue(task.priority,
                       "La tâche doit être marquée comme prioritaire")
        self.assertEqual(task.title, "Tâche URGENTE")
    
    @tc("TP004")
    def test_task_form_includes_priority_field(self):
        """TP004: Test que TaskForm inclut le champ priority."""
        form = TaskForm()
        self.assertIn('priority', form.fields,
                     "TaskForm doit inclure le champ 'priority'")
    
    @tc("TP005")
    def test_priority_in_create_view(self):
        """TP005: Test que la vue de création accepte la priorité."""
        # POST sur l'URL de liste (qui gère la création)
        response = self.client.post(reverse('list'), {
            'title': 'Tâche importante',
            'priority': 'on'  # Les checkboxes envoient 'on' quand cochées
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        
        # Vérifier que la tâche a été créée avec priorité
        task = Task.objects.last()
        self.assertEqual(task.title, 'Tâche importante')
        self.assertTrue(task.priority)
    
    @tc("TP006")
    def test_tasks_ordered_by_priority(self):
        """TP006: Test que les tâches sont ordonnées par priorité."""
        # Créer des tâches dans un ordre spécifique
        Task.objects.create(title="Tâche 1 (normale)", priority=False)
        Task.objects.create(title="Tâche 2 (urgente)", priority=True)
        Task.objects.create(title="Tâche 3 (normale)", priority=False)
        Task.objects.create(title="Tâche 4 (urgente)", priority=True)
        
        # Récupérer dans l'ordre attendu (prioritaires d'abord)
        tasks = Task.objects.all().order_by('-priority')
        
        # Vérifier l'ordre
        self.assertTrue(tasks[0].priority)  # Première = prioritaire
        self.assertTrue(tasks[1].priority)  # Deuxième = prioritaire
        self.assertFalse(tasks[2].priority) # Troisième = normale
        self.assertFalse(tasks[3].priority) # Quatrième = normale
    
    @tc("TP007")
    def test_priority_display_in_template(self):
        """TP007: Test que la priorité s'affiche dans le template."""
        task = Task.objects.create(title="Tâche test", priority=True)
        response = self.client.get(reverse('list'))
        self.assertContains(response, "Tâche test")
        # Après implémentation, on vérifiera l'indicateur visuel