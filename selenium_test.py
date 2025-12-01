#!/usr/bin/env python3
"""
Tests E2E avec Selenium pour l'application To-Do List.
Exercice 9 - Générer result_test_selenium.json
"""

import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TodoListSeleniumTests:
    """Tests E2E automatisés avec Selenium."""
    
    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.driver = None
        self.results = {}
        
    def setup(self):
        """Initialise le driver Selenium."""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Exécution sans interface graphique
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.implicitly_wait(10)
        
    def teardown(self):
        """Ferme le driver."""
        if self.driver:
            self.driver.quit()
    
    def test_count_create_delete_tasks(self):
        """Test E2E complet : compter, créer 10 tâches, supprimer 10 tâches."""
        test_id = "TE001"
        try:
            print(f"🧪 Exécution du test {test_id}...")
            
            # Étape 1: Accéder à l'application
            self.driver.get(self.base_url)
            assert "TO DO LIST" in self.driver.title, "Page d'accueil non chargée"
            
            # Étape 2: Compter les tâches initiales
            initial_count = self.count_tasks()
            print(f"   Nombre initial de tâches: {initial_count}")
            
            # Étape 3: Créer 10 tâches
            created_tasks = []
            for i in range(10):
                task_name = f"Tâche Selenium {i+1}"
                self.create_task(task_name)
                created_tasks.append(task_name)
                print(f"   Créée: {task_name}")
                time.sleep(0.5)  # Petite pause
            
            # Étape 4: Compter après création
            after_create_count = self.count_tasks()
            print(f"   Nombre après création: {after_create_count}")
            assert after_create_count == initial_count + 10, "Les 10 tâches n'ont pas été créées"
            
            # Étape 5: Supprimer les 10 tâches créées
            for task_name in created_tasks:
                self.delete_task(task_name)
                print(f"   Supprimée: {task_name}")
                time.sleep(0.5)
            
            # Étape 6: Compter après suppression
            final_count = self.count_tasks()
            print(f"   Nombre final: {final_count}")
            assert final_count == initial_count, "Le nombre final ne correspond pas au nombre initial"
            
            print(f"✅ Test {test_id} réussi!")
            self.results[test_id] = {
                "status": "passed",
                "message": f"Test E2E réussi: {initial_count} -> {after_create_count} -> {final_count} tâches"
            }
            
        except Exception as e:
            print(f"❌ Test {test_id} échoué: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }
    
    def test_add_delete_specific_task(self):
        """Test E2E spécifique: ajouter, identifier, ajouter autre, supprimer dernière."""
        test_id = "TE002"
        try:
            print(f"🧪 Exécution du test {test_id}...")
            
            # Étape 1: Accéder à l'application
            self.driver.get(self.base_url)
            
            # Étape 2: Ajouter une première tâche et sauvegarder son nom
            first_task_name = "Première tâche importante"
            self.create_task(first_task_name)
            print(f"   Première tâche créée: {first_task_name}")
            time.sleep(1)
            
            # Étape 3: Vérifier qu'elle est présente
            assert self.is_task_present(first_task_name), "La première tâche n'est pas présente"
            
            # Étape 4: Ajouter une deuxième tâche
            second_task_name = "Deuxième tâche à supprimer"
            self.create_task(second_task_name)
            print(f"   Deuxième tâche créée: {second_task_name}")
            time.sleep(1)
            
            # Étape 5: Supprimer la deuxième tâche
            self.delete_task(second_task_name)
            print(f"   Deuxième tâche supprimée: {second_task_name}")
            time.sleep(1)
            
            # Étape 6: Vérifier que la première est toujours présente
            assert self.is_task_present(first_task_name), "La première tâche a disparu"
            
            # Étape 7: Vérifier que la deuxième n'est plus présente
            assert not self.is_task_present(second_task_name), "La deuxième tâche est toujours présente"
            
            print(f"✅ Test {test_id} réussi!")
            self.results[test_id] = {
                "status": "passed",
                "message": "Test spécifique réussi: première tâche persistante"
            }
            
        except Exception as e:
            print(f"❌ Test {test_id} échoué: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }
    
    def count_tasks(self):
        """Compte le nombre de tâches affichées."""
        try:
            # Cherche tous les éléments de tâche (adaptez ce sélecteur à votre HTML)
            tasks = self.driver.find_elements(By.CSS_SELECTOR, ".task-item, tr.task, li.task, .task")
            return len(tasks)
        except:
            return 0
    
    def create_task(self, task_name):
        """Crée une nouvelle tâche."""
        # Trouve le champ de saisie (adaptez ce sélecteur)
        input_field = self.driver.find_element(By.NAME, "title")
        input_field.clear()
        input_field.send_keys(task_name)
        
        # Trouve et clique sur le bouton d'ajout
        submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")
        submit_button.click()
        
        time.sleep(0.5)  # Attente pour le rechargement
    
    def delete_task(self, task_name):
        """Supprime une tâche par son nom."""
        try:
            # Trouve la tâche (cette logique dépend de votre structure HTML)
            # Exemple: chercher un lien/button de suppression à côté du texte de la tâche
            task_elements = self.driver.find_elements(By.XPATH, f"//*[contains(text(), '{task_name}')]")
            
            for element in task_elements:
                # Chercher le bouton de suppression à proximité
                try:
                    delete_btn = element.find_element(By.XPATH, "./following::a[contains(@href, 'delete') or contains(text(), 'Supprimer') or contains(text(), 'Delete')] | ./following::button[contains(text(), 'Supprimer') or contains(text(), 'Delete')]")
                    if delete_btn:
                        delete_btn.click()
                        time.sleep(0.5)
                        
                        # Confirmer la suppression si nécessaire
                        try:
                            confirm_btn = self.driver.find_element(By.CSS_SELECTOR, "button.confirm-delete, input[value='Confirm'], input[value='Confirmer'], button[type='submit']")
                            confirm_btn.click()
                        except:
                            pass
                        
                        break
                except:
                    continue
        except Exception as e:
            print(f"   Erreur lors de la suppression de '{task_name}': {e}")
    
    def is_task_present(self, task_name):
        """Vérifie si une tâche est présente."""
        try:
            self.driver.find_element(By.XPATH, f"//*[contains(text(), '{task_name}')]")
            return True
        except:
            return False
    
    def save_results(self):
        """Sauvegarde les résultats dans un fichier JSON."""
        output_file = "result_test_selenium.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n📁 Résultats sauvegardés dans: {output_file}")
        
        # Afficher le résumé
        passed = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        
        print("\n📈 RÉSUMÉ TESTS SELENIUM:")
        print(f"   ✅ Tests passés: {passed}")
        print(f"   ❌ Tests échoués: {failed}")
        print(f"   📊 Total: {len(self.results)}")

def run_selenium_tests():
    """Exécute tous les tests Selenium."""
    tester = TodoListSeleniumTests()
    
    try:
        print("🚀 Lancement des tests Selenium E2E...")
        tester.setup()
        
        # Exécuter les tests
        tester.test_count_create_delete_tasks()
        tester.test_add_delete_specific_task()
        
        # Sauvegarder les résultats
        tester.save_results()
        
    finally:
        tester.teardown()
    
    return tester.results

if __name__ == "__main__":
    print("="*60)
    print("EXÉCUTION DES TESTS SELENIUM - EXERCICE 9")
    print("="*60)
    results = run_selenium_tests()
    print("\n🎯 Tests Selenium terminés. Vérifiez result_test_selenium.json")
    print("="*60)
    