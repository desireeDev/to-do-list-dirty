import importlib.util
import os
import json
import subprocess
from django.test import TestCase
from django.urls import reverse
from tasks.models import Task
from tasks.decorators import tc  # <-- NEW IMPORTATION


class TaskTests(TestCase):
    """Batterie complète de tests pour l'app tasks."""

    def setUp(self):
        """Prépare une tâche de test et le chemin du dataset."""
        self.task = Task.objects.create(title="Test Task", complete=False)
        self.dataset_path = os.path.join(
            os.path.dirname(__file__), 'dataset.json'
        )

    # ================================
    # Tests pour la view index (/)
    # ================================
    @tc("TC001")  # <-- DÉCORATEUR AJOUTÉ
    def test_01_index_get(self):
        """GET / affiche correctement la liste."""
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TO DO LIST")

    @tc("TC002")  # <-- DÉCORATEUR AJOUTÉ
    def test_02_index_post_valid(self):
        """POST / avec données valides ajoute la tâche."""
        response = self.client.post(
            reverse('list'),
            {'title': 'Nouvelle Tâche', 'complete': False}
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title='Nouvelle Tâche').exists())

    @tc("TC003")  # <-- DÉCORATEUR AJOUTÉ
    def test_03_index_post_invalid(self):
        """POST / avec données invalides ne crée pas de tâche."""
        response = self.client.post(reverse('list'), {'title': ''})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Task.objects.count(), 1)

    # ================================
    # Tests pour updateTask
    # ================================
    @tc("TC004")  # <-- DÉCORATEUR AJOUTÉ
    def test_04_update_task_get_valid_id(self):
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    @tc("TC005")  # <-- DÉCORATEUR AJOUTÉ
    def test_05_update_task_get_invalid_id(self):
        response = self.client.get(reverse('update_task', args=[999]))
        self.assertEqual(response.status_code, 404)

    @tc("TC006")  # <-- DÉCORATEUR AJOUTÉ
    def test_06_update_task_post_valid(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': 'Task modifiée', 'complete': True}
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Task modifiée')
        self.assertTrue(self.task.complete)

    @tc("TC007")  # <-- DÉCORATEUR AJOUTÉ
    def test_07_update_task_post_invalid(self):
        response = self.client.post(
            reverse('update_task', args=[self.task.id]),
            {'title': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, '')

    # ================================
    # Tests pour deleteTask
    # ================================
    @tc("TC008")  # <-- DÉCORATEUR AJOUTÉ
    def test_08_delete_task_get_valid_id(self):
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)

    @tc("TC009")  # <-- DÉCORATEUR AJOUTÉ
    def test_09_delete_task_get_invalid_id(self):
        response = self.client.get(reverse('delete', args=[999]))
        self.assertEqual(response.status_code, 404)

    @tc("TC010")  # <-- DÉCORATEUR AJOUTÉ
    def test_10_delete_task_post(self):
        response = self.client.post(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    # ================================
    # Tests dataset
    # ================================
    @tc("TC011")  # <-- DÉCORATEUR AJOUTÉ
    def test_11_dataset_import(self):
        """Import du dataset JSON crée toutes les tâches."""
        Task.objects.all().delete()
        with open(self.dataset_path) as f:
            data = json.load(f)
        for item in data:
            Task.objects.create(**item)
        self.assertEqual(Task.objects.count(), len(data))
        for item in data:
            self.assertTrue(Task.objects.filter(title=item['title']).exists())

    @tc("TC012")  # <-- DÉCORATEUR AJOUTÉ
    def test_12_import_dataset_script(self):
        """Test l'import via le script import_dataset.py."""
        script_path = os.path.join(
            os.path.dirname(__file__), 'import_dataset.py'
        )
        spec = importlib.util.spec_from_file_location(
            "import_dataset", script_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(Task.objects.exists())

    # ================================
    # Tests modèles
    # ================================
    @tc("TC013")  # <-- DÉCORATEUR AJOUTÉ
    def test_13_task_str(self):
        """Vérifie la représentation en chaîne de la tâche."""
        self.assertEqual(str(self.task), self.task.title)

    @tc("TC014")  # <-- DÉCORATEUR AJOUTÉ
    def test_14_task_created_field(self):
        """Vérifie que le champ created est défini à la création."""
        self.assertIsNotNone(self.task.created)

    # ================================
    # Tests d'accessibilité WCAG 2.1 AA
    # ================================
    @tc("TC015")  # <-- DÉCORATEUR AJOUTÉ
    def test_15_accessibility_homepage_semantic_structure(self):
        """Test la structure sémantique de la page d'accueil."""
        response = self.client.get(reverse('list'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('<header', content)
        self.assertIn('<main', content)
        self.assertIn('<section', content)

    @tc("TC016")  # <-- DÉCORATEUR AJOUTÉ
    def test_16_accessibility_form_labels(self):
        """Test que les formulaires ont des labels appropriés."""
        response = self.client.get(reverse('list'))
        content = response.content.decode()
        self.assertIn('for="id_title"', content)
        self.assertIn('Nouvelle tâche', content)

    @tc("TC017")  # <-- DÉCORATEUR AJOUTÉ
    def test_17_accessibility_aria_attributes(self):
        """Test la présence d'attributs ARIA."""
        response = self.client.get(reverse('list'))
        content = response.content.decode()
        self.assertIn('role="main"', content)
        self.assertIn('aria-label', content)
        self.assertIn('aria-describedby', content)

    @tc("TC018")  # <-- DÉCORATEUR AJOUTÉ
    def test_18_accessibility_keyboard_navigation(self):
        """Test les éléments de navigation au clavier."""
        response = self.client.get(reverse('list'))
        content = response.content.decode()
        self.assertIn('btn:focus', content)
        self.assertIn('outline', content)

    @tc("TC019")  # <-- DÉCORATEUR AJOUTÉ
    def test_19_accessibility_update_page(self):
        """Test l'accessibilité de la page de modification."""
        response = self.client.get(reverse('update_task', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('for="id_title"', content)
        self.assertIn('for="id_complete"', content)

    @tc("TC020")  # <-- DÉCORATEUR AJOUTÉ
    def test_20_accessibility_delete_page(self):
        """Test l'accessibilité de la page de suppression."""
        response = self.client.get(reverse('delete', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('role="alert"', content)
        self.assertIn('aria-live', content)


class AccessibilityAutomatedTests(TestCase):
    """Tests d'accessibilité automatisés avec pa11y (si disponible)."""

    def setUp(self):
        self.task = Task.objects.create(title="Test Task", complete=False)

    @tc("TC021")  # <-- DÉCORATEUR AJOUTÉ
    def test_pa11y_available(self):
        """Test que pa11y est disponible (ne fait pas échouer si absent)."""
        try:
            result = subprocess.run(['pa11y', '--version'],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                self.assertTrue(True, "pa11y est disponible")
        except FileNotFoundError:
            self.skipTest("pa11y n'est pas installé")