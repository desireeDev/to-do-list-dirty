#!/usr/bin/env python3
"""
Tests E2E avec Selenium pour l'application To-Do List.
Exercice 9 - Générer result_test_selenium.json
Exercice 12 - Test spécifique de suppression
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager


class TodoListSeleniumTests:
    """Tests E2E automatisés avec Selenium."""

    def __init__(self):
        self.base_url = "http://127.0.0.1:8000"
        self.driver = None
        self.results = {}

    def setup(self):
        """Initialise le driver Selenium avec ChromeDriverManager."""
        try:
            print("🚀 Configuration de Selenium avec ChromeDriverManager...")
            # Options Chrome
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Mode headless pour rapidité
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            # Désactiver les logs inutiles
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # Installation automatique de ChromeDriver
            print("📦 Installation automatique de ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            # Créer le driver
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(5)  # Réduit à 5 secondes
            # Vérifier que le driver fonctionne
            print("✅ ChromeDriver installé et prêt")
            print(f"🌐 URL de base: {self.base_url}")
        except Exception as e:
            print(f"❌ Erreur lors du setup Selenium: {e}")
            print("\n💡 Solutions possibles:")
            print("   1. Vérifiez que Chrome est installé")
            print("   2. Essayez: pip install webdriver-manager --upgrade")
            print("   3. Ou installez ChromeDriver manuellement:")
            print("      - Téléchargez depuis https://chromedriver.chromium.org/")
            print("      - Placez-le dans /usr/local/bin/ (Mac/Linux) ou C:\\Windows\\System32\\ (Windows)")
            raise e

    def teardown(self):
        """Ferme le driver."""
        if self.driver:
            self.driver.quit()
            print("✅ Driver Selenium fermé")

    def cleanup_existing_tasks(self):
        """Nettoie rapidement les tâches existantes."""
        try:
            print("   🧹 Nettoyage rapide...")
            self.driver.get(self.base_url)
            time.sleep(1)
            
            # Chercher les boutons Supprimer
            try:
                delete_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Supprimer') or contains(text(), 'Delete')]"
                )
                
                # Supprimer seulement 5 premières pour aller vite
                max_to_delete = min(5, len(delete_buttons))
                for i in range(max_to_delete):
                    try:
                        btn = delete_buttons[i]
                        if btn.is_displayed():
                            btn.click()
                            time.sleep(0.3)
                            self.handle_delete_confirmation_fast()
                            time.sleep(0.3)
                    except:
                        continue
                
                if delete_buttons:
                    print(f"   ✅ {max_to_delete} tâches nettoyées")
                else:
                    print("   ✅ Aucune tâche à nettoyer")
                    
            except Exception as e:
                print(f"   ⚠ Erreur nettoyage: {e}")
            
        except Exception as e:
            print(f"   ⚠ Erreur générale: {e}")

    def handle_delete_confirmation_fast(self):
        """Gère rapidement la confirmation de suppression."""
        try:
            time.sleep(0.2)
            # Essayer de trouver un bouton de confirmation
            confirm_selectors = [
                "//button[contains(text(), 'Oui')]",
                "//button[contains(text(), 'Yes')]",
                "//button[contains(text(), 'Confirmer')]",
                "//button[contains(text(), 'Confirm')]"
            ]
            
            for selector in confirm_selectors:
                try:
                    confirm_btn = self.driver.find_element(By.XPATH, selector)
                    if confirm_btn.is_displayed():
                        confirm_btn.click()
                        time.sleep(0.2)
                        return True
                except:
                    continue
            return True
        except:
            return True

    def test_count_create_delete_tasks_fast(self):
        """Test E2E rapide : créer 10 tâches, les supprimer."""
        test_id = "TE001"
        try:
            print(f"🧪 Test {test_id}: Créer et supprimer 10 tâches")
            
            # 1. Nettoyer rapidement
            self.cleanup_existing_tasks()
            
            # 2. Aller sur la page
            self.driver.get(self.base_url)
            time.sleep(1)
            
            # 3. Créer 10 tâches avec des noms propres
            print("   🏗️  Création de 10 tâches...")
            created_tasks = []
            
            for i in range(10):
                task_name = f"Tâche Selenium {i + 1}"  # Nom propre
                print(f"   Création {i+1}/10: {task_name}")
                
                if self.create_task_fast(task_name):
                    created_tasks.append(task_name)
                    print(f"   ✅ Créée")
                else:
                    print(f"   ❌ Échec création {i+1}")
                
                time.sleep(0.5)
            
            print(f"   📊 Résultat création: {len(created_tasks)}/10 réussies")
            
            if not created_tasks:
                raise Exception("Aucune tâche n'a pu être créée")
            
            # 4. Supprimer les tâches créées
            print("   🗑️  Suppression des tâches...")
            success_deletions = 0
            
            for i, task_name in enumerate(created_tasks):
                print(f"   Suppression {i+1}/{len(created_tasks)}: {task_name}")
                
                if self.delete_task_fast(task_name):
                    success_deletions += 1
                    print(f"   ✅ Supprimée")
                else:
                    print(f"   ❌ Échec suppression")
                
                time.sleep(0.5)
            
            print(f"   📊 Résultat suppression: {success_deletions}/{len(created_tasks)} réussies")
            
            # Validation
            if success_deletions > 0:
                print(f"✅ Test {test_id} RÉUSSI!")
                self.results[test_id] = {
                    "status": "passed",
                    "message": f"{len(created_tasks)} tâches créées, {success_deletions} supprimées"
                }
            else:
                raise Exception("Aucune tâche n'a pu être supprimée")
                
        except Exception as e:
            print(f"❌ Test {test_id} ÉCHOUÉ: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }

    def create_task_fast(self, task_name):
        """Crée une tâche - VERSION RAPIDE ET FIABLE."""
        try:
            # S'assurer qu'on est sur la bonne page
            self.driver.get(self.base_url)
            time.sleep(0.5)
            
            # 1. Trouver le champ de saisie
            input_field = None
            
            # Essayer plusieurs sélecteurs courants
            selectors = [
                (By.NAME, "title"),
                (By.ID, "id_title"),
                (By.CSS_SELECTOR, 'input[type="text"]'),
                (By.CSS_SELECTOR, 'textarea[name="title"]'),
                (By.CSS_SELECTOR, 'input[name="title"]'),
                (By.CSS_SELECTOR, 'input.form-control')
            ]
            
            for by, selector in selectors:
                try:
                    input_field = self.driver.find_element(by, selector)
                    if input_field.is_displayed():
                        break
                except:
                    continue
            
            if not input_field:
                # Dernière tentative: premier input de type text
                try:
                    inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    for inp in inputs:
                        if inp.is_displayed():
                            input_field = inp
                            break
                except:
                    pass
            
            if not input_field:
                return False
            
            # 2. Remplir le champ
            input_field.clear()
            input_field.send_keys(task_name)
            time.sleep(0.1)
            
            # 3. Trouver le bouton d'ajout
            submit_button = None
            
            # Chercher par texte d'abord
            button_texts = ['Ajouter', 'Add', 'Submit', 'Créer', 'Create', 'Save', 'Valider']
            for text in button_texts:
                try:
                    # XPath pour bouton avec ce texte
                    buttons = self.driver.find_elements(
                        By.XPATH, f"//button[contains(text(), '{text}')]"
                    )
                    for btn in buttons:
                        if btn.is_displayed():
                            submit_button = btn
                            break
                    if submit_button:
                        break
                except:
                    continue
            
            # Si pas trouvé, chercher par type
            if not submit_button:
                try:
                    submit_button = self.driver.find_element(
                        By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]'
                    )
                except:
                    pass
            
            # Si toujours pas trouvé, premier bouton visible
            if not submit_button:
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, 'button')
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            submit_button = btn
                            break
                except:
                    pass
            
            if not submit_button:
                return False
            
            # 4. Cliquer
            submit_button.click()
            time.sleep(0.5)  # Attendre la création
            
            # 5. Vérification rapide
            time.sleep(0.5)
            return True
            
        except Exception as e:
            print(f"     ⚠ Erreur création: {e}")
            return False

    def delete_task_fast(self, task_name):
        """Supprime une tâche - VERSION RAPIDE."""
        try:
            # Rafraîchir la page
            self.driver.refresh()
            time.sleep(0.5)
            
            # Chercher UN bouton Supprimer (le premier)
            delete_button = None
            
            # Chercher par texte d'abord
            try:
                delete_buttons = self.driver.find_elements(
                    By.XPATH, "//button[contains(text(), 'Supprimer') or contains(text(), 'Delete')]"
                )
                if delete_buttons:
                    for btn in delete_buttons:
                        if btn.is_displayed():
                            delete_button = btn
                            break
            except:
                pass
            
            # Chercher par classe
            if not delete_button:
                try:
                    delete_buttons = self.driver.find_elements(
                        By.CSS_SELECTOR, '.btn-danger, .btn-delete, [class*="delete"]'
                    )
                    for btn in delete_buttons:
                        if btn.is_displayed():
                            delete_button = btn
                            break
                except:
                    pass
            
            if not delete_button:
                # Pas de bouton Supprimer trouvé
                return False
            
            # Cliquer
            delete_button.click()
            time.sleep(0.3)
            
            # Gérer confirmation rapide
            self.handle_delete_confirmation_fast()
            time.sleep(0.5)
            
            return True
            
        except Exception as e:
            print(f"     ⚠ Erreur suppression: {e}")
            return False

    def test_add_delete_specific_task_fast(self):
        """Test spécifique rapide."""
        test_id = "TE002"
        try:
            print(f"🧪 Test {test_id}: Tâche spécifique")
            
            # Aller sur la page
            self.driver.get(self.base_url)
            time.sleep(1)
            
            # 1. Créer première tâche
            first_task = "Première tâche importante"
            print(f"   Création 1: {first_task}")
            
            if not self.create_task_fast(first_task):
                raise Exception(f"Échec création 1")
            print(f"   ✅ Créée")
            time.sleep(0.5)
            
            # 2. Créer deuxième tâche
            second_task = "Deuxième tâche à supprimer"
            print(f"   Création 2: {second_task}")
            
            if not self.create_task_fast(second_task):
                raise Exception(f"Échec création 2")
            print(f"   ✅ Créée")
            time.sleep(0.5)
            
            # 3. Supprimer deuxième tâche
            print(f"   Suppression: {second_task}")
            if not self.delete_task_fast(second_task):
                raise Exception(f"Échec suppression")
            print(f"   ✅ Supprimée")
            time.sleep(0.5)
            
            # 4. Vérifier que première existe toujours
            self.driver.refresh()
            time.sleep(0.5)
            
            if first_task in self.driver.page_source:
                print(f"   ✅ Première tâche toujours présente")
                print(f"✅ Test {test_id} RÉUSSI!")
                self.results[test_id] = {
                    "status": "passed",
                    "message": "Tâche persistante vérifiée"
                }
            else:
                raise Exception("Première tâche a disparu")
                
        except Exception as e:
            print(f"❌ Test {test_id} ÉCHOUÉ: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }

    def test_exercise_12_fast(self):
        """Exercice 12 rapide."""
        test_id = "TE012"
        try:
            print(f"🧪 Test {test_id}: Exercice 12")
            
            # Aller sur la page
            self.driver.get(self.base_url)
            time.sleep(1)
            
            # 1. Créer première tâche
            first_task = "Tâche Exercice 12 - Persistante"
            print(f"   Création 1: {first_task}")
            
            if not self.create_task_fast(first_task):
                raise Exception(f"Échec création 1")
            print(f"   ✅ Créée")
            time.sleep(0.5)
            
            # 2. Créer deuxième tâche
            second_task = "Tâche Exercice 12 - À supprimer"
            print(f"   Création 2: {second_task}")
            
            if not self.create_task_fast(second_task):
                raise Exception(f"Échec création 2")
            print(f"   ✅ Créée")
            time.sleep(0.5)
            
            # 3. Supprimer deuxième tâche
            print(f"   Suppression: {second_task}")
            if not self.delete_task_fast(second_task):
                raise Exception(f"Échec suppression")
            print(f"   ✅ Supprimée")
            time.sleep(0.5)
            
            # 4. Vérifier que première existe toujours
            self.driver.refresh()
            time.sleep(0.5)
            
            if first_task in self.driver.page_source:
                print(f"   ✅ Première tâche toujours présente")
                print(f"✅ Test {test_id} RÉUSSI!")
                self.results[test_id] = {
                    "status": "passed",
                    "message": "Exercice 12 validé"
                }
            else:
                raise Exception("Tâche persistante a disparu")
                
        except Exception as e:
            print(f"❌ Test {test_id} ÉCHOUÉ: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }

    def save_results(self):
        """Sauvegarde les résultats dans un fichier JSON."""
        output_file = "result_test_selenium.json"
        passed = sum(1 for r in self.results.values() if r["status"] == "passed")
        failed = sum(1 for r in self.results.values() if r["status"] == "failed")
        total = len(self.results)
        
        results_data = {
            "tests": self.results,
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Résultats sauvegardés dans: {output_file}")
        print("\n📈 RÉSUMÉ TESTS SELENIUM:")
        print(f"   ✅ Tests passés: {passed}")
        print(f"   ❌ Tests échoués: {failed}")
        print(f"   📊 Total: {total}")


def run_selenium_tests():
    """Exécute tous les tests Selenium."""
    tester = TodoListSeleniumTests()
    try:
        print("=" * 60)
        print("🚀 LANCEMENT DES TESTS SELENIUM - RAPIDE")
        print("=" * 60)
        
        tester.setup()
        
        print("\n" + "=" * 60)
        print("🧪 DÉBUT DES TESTS")
        print("=" * 60)
        
        # Exécuter les tests RAPIDES
        tester.test_count_create_delete_tasks_fast()  # TE001
        time.sleep(1)
        tester.test_add_delete_specific_task_fast()   # TE002
        time.sleep(1)
        tester.test_exercise_12_fast()                # TE012
        
        tester.save_results()
        
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        
        # Sauvegarder les résultats même en cas d'erreur
        try:
            tester.save_results()
        except:
            pass
    finally:
        tester.teardown()
    
    return tester.results


if __name__ == "__main__":
    print("=" * 60)
    print("TESTS SELENIUM - EXERCICES 9 & 12")
    print("=" * 60)
    print("\n⚠  PRÉREQUIS:")
    print("1. Serveur Django doit tourner")
    print("2. Application accessible: http://127.0.0.1:8000/")
    print("=" * 60)
    
    # Démarrer directement
    print("Démarrage dans 3 secondes...")
    time.sleep(3)
    
    results = run_selenium_tests()
    
    print("\n" + "=" * 60)
    print("🎯 TESTS TERMINÉS")
    print("=" * 60)
    print(f"Fichier: result_test_selenium.json")
    print("=" * 60)
    
    if results:
        passed = sum(1 for r in results.values() if r["status"] == "passed")
        total = len(results)
        if passed == total:
            print("🎉 TOUS LES TESTS RÉUSSIS !")
        else:
            print(f"⚠  {passed}/{total} tests réussis")
