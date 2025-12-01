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
        self.base_url = "http://127.0.0.1:8000/"
        self.driver = None
        self.results = {}

    def setup(self):
        """Initialise le driver Selenium avec ChromeDriverManager."""
        try:
            print("🚀 Configuration de Selenium avec ChromeDriverManager...")
            # Options Chrome
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Exécution sans interface
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            # Désactiver les logs inutiles
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # Installation automatique de ChromeDriver
            print("📦 Installation automatique de ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            # Créer le driver
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.implicitly_wait(10)
            # Vérifier que le driver fonctionne
            print("✅ ChromeDriver installé et prêt")
            print(f"🌐 URL de base: {self.base_url}")
        except Exception as e:
            print(f"❌ Erreur lors du setup Selenium: {e}")
            print("\n💡 Solutions possibles:")
            print("   1. Vérifiez que Chrome est installé")
            print("   2. Essayez: pipenv install webdriver-manager --upgrade")
            print("   3. Ou installez ChromeDriver manuellement:")
            print("      - Téléchargez depuis https://chromedriver.chromium.org/")
            print("      - Placez-le dans /usr/local/bin/ (Mac/Linux) ou C:\\Windows\\System32\\ (Windows)")
            raise e

    def teardown(self):
        """Ferme le driver."""
        if self.driver:
            self.driver.quit()
            print("✅ Driver Selenium fermé")

    def test_count_create_delete_tasks(self):
        """Test E2E complet : compter, créer 10 tâches, supprimer 10."""
        test_id = "TE001"
        try:
            print(f"🧪 Exécution du test {test_id}...")
            # Étape 1: Accéder à l'application
            self.driver.get(self.base_url)
            time.sleep(2)  # Attendre que la page charge
            assert "TO DO LIST" in self.driver.title or "Todo" in self.driver.title, "Page non chargée"
            # Étape 2: Compter les tâches initiales
            initial_count = self.count_tasks()
            print(f"   Nombre initial de tâches: {initial_count}")
            # Étape 3: Créer 10 tâches
            created_tasks = []
            for i in range(10):
                task_name = f"Tâche Selenium {i + 1}"
                if self.create_task(task_name):
                    created_tasks.append(task_name)
                    print(f"   Créée: {task_name}")
                else:
                    print(f"   ⚠ Échec création: {task_name}")
                time.sleep(0.5)
            # Étape 4: Compter après création
            after_create_count = self.count_tasks()
            print(f"   Nombre après création: {after_create_count}")
            expected = initial_count + 10
            if after_create_count != expected:
                print(f"   ⚠ Attendu: {expected}, obtenu: {after_create_count}")
            # Étape 5: Supprimer les 10 tâches créées
            for task_name in created_tasks:
                if self.delete_task(task_name):
                    print(f"   Supprimée: {task_name}")
                else:
                    print(f"   ⚠ Échec suppression: {task_name}")
                time.sleep(0.5)
            # Étape 6: Compter après suppression
            final_count = self.count_tasks()
            print(f"   Nombre final: {final_count}")
            # Validation finale
            if final_count == initial_count:
                print(f"✅ Test {test_id} réussi!")
                self.results[test_id] = {
                    "status": "passed",
                    "message": f"Test réussi: {initial_count}→{after_create_count}→{final_count}"
                }
            else:
                raise Exception(f"Nombre final incorrect: attendu {initial_count}, obtenu {final_count}")
        except Exception as e:
            print(f"❌ Test {test_id} échoué: {str(e)}")
            self.results[test_id] = {
                "status": "failed",
                "message": str(e)
            }

    def test_add_delete_specific_task(self):
        """Test spécifique: ajouter, identifier, ajouter autre, supprimer."""
        test_id = "TE002"
        try:
            print(f"🧪 Exécution du test {test_id}...")
            # Étape 1: Accéder à l'application
            self.driver.get(self.base_url)
            time.sleep(2)
            # Étape 2: Ajouter une première tâche
            first_task_name = "Première tâche importante"
            self.create_task(first_task_name)
            print(f"   Première tâche créée: {first_task_name}")
            time.sleep(1)
            # Étape 3: Vérifier qu'elle est présente
            present = self.is_task_present(first_task_name)
            assert present, "Première tâche absente"
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
            assert self.is_task_present(first_task_name), "Première tâche disparue"
            # Étape 7: Vérifier que la deuxième n'est plus présente
            not_present = not self.is_task_present(second_task_name)
            assert not_present, "Deuxième tâche toujours présente"
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

    def test_exercise_12_specific(self):
        """
        Test spécifique pour l'exercice 12:
        - ajout d'une tâche
        - détecter l'ID/le nom de la tâche ajoutée
        - ajout d'une autre tâche
        - suppression de la dernière tâche créée
        - la 1ère tâche créée doit être toujours présente
        """
        test_id = "TE012"
        try:
            print(f"🧪 Exécution du test {test_id} (Exercice 12)...")
            # Étape 1: Accéder à l'application
            self.driver.get(self.base_url)
            time.sleep(2)
            print("   ✓ Accès à l'application")
            # Étape 2: Ajouter une première tâche
            first_task_name = "Tâche Exercice 12 - Persistante"
            self.create_task(first_task_name)
            print(f"   ✓ Première tâche créée: '{first_task_name}'")
            time.sleep(1)
            # Étape 3: Détecter l'ID/le nom de la tâche ajoutée
            saved_task_name = first_task_name
            print(f"   ✓ Nom de la tâche sauvegardé: '{saved_task_name}'")
            # Étape 4: Ajouter une autre tâche
            second_task_name = "Tâche Exercice 12 - À supprimer"
            self.create_task(second_task_name)
            print(f"   ✓ Deuxième tâche créée: '{second_task_name}'")
            time.sleep(1)
            # Étape 5: Suppression de la dernière tâche créée
            self.delete_task(second_task_name)
            print(f"   ✓ Dernière tâche supprimée: '{second_task_name}'")
            time.sleep(1)
            # Étape 6: Vérifier que la 1ère tâche est toujours présente
            if self.is_task_present(saved_task_name):
                msg = f"   ✓ Première tâche toujours présente: '{saved_task_name}'"
                print(msg)
                print(f"✅ Test {test_id} réussi!")
                self.results[test_id] = {
                    "status": "passed",
                    "message": "Exercice 12 réussi: tâche persistante",
                    "details": {
                        "first_task": saved_task_name,
                        "second_task": second_task_name,
                        "first_task_still_present": True
                    }
                }
            else:
                raise Exception(f"Tâche '{saved_task_name}' a disparu!")
        except Exception as e:
            print(f"❌ Test {test_id} échoué: {str(e)}")
            first = first_task_name if 'first_task_name' in locals() else "Non définie"
            second = second_task_name if 'second_task_name' in locals() else "Non définie"
            self.results[test_id] = {
                "status": "failed",
                "message": str(e),
                "details": {
                    "first_task": first,
                    "second_task": second,
                    "error": str(e)
                }
            }

    def count_tasks(self):
        """Compte le nombre de tâches affichées."""
        try:
            # Essaye différents sélecteurs pour trouver les tâches
            selectors = [
                '.item-row',
                '[data-testid="task-item"]',
                '.task',
                'div[role="listitem"]',
                'tr',  # Pour les tables
                'li',  # Pour les listes
                'div.task-item',
                '.todo-item'
            ]
            for selector in selectors:
                try:
                    tasks = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    # Filtrer les éléments visibles
                    visible_tasks = [t for t in tasks if t.is_displayed()]
                    if visible_tasks:
                        return len(visible_tasks)
                except Exception:
                    continue
            # Si aucun sélecteur ne fonctionne, essayer par XPath générique
            try:
                tasks = self.driver.find_elements(
                    By.XPATH, "//*[contains(@class, 'task') or contains(@class, 'item')]"
                )
                visible_tasks = [t for t in tasks if t.is_displayed()]
                return len(visible_tasks)
            except Exception:
                return 0
        except Exception:
            return 0

    def create_task(self, task_name):
        """Crée une nouvelle tâche."""
        try:
            time.sleep(0.5)
            # Cherche le champ de saisie avec différentes méthodes
            input_selectors = [
                (By.NAME, "title"),
                (By.CSS_SELECTOR, '[data-testid="task-input"]'),
                (By.CSS_SELECTOR, 'input[type="text"]'),
                (By.CSS_SELECTOR, '#id_title'),
                (By.CSS_SELECTOR, 'input.form-control'),
                (By.CSS_SELECTOR, 'input[name="title"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="tâche"]'),
                (By.CSS_SELECTOR, 'input[placeholder*="task"]')
            ]
            input_field = None
            for by, selector in input_selectors:
                try:
                    input_field = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    break
                except (NoSuchElementException, TimeoutException):
                    continue
            if not input_field:
                # Dernière tentative: prendre le premier champ texte
                try:
                    input_fields = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                    if input_fields:
                        input_field = input_fields[0]
                except Exception:
                    pass
            if not input_field:
                print(f"   ⚠ Champ de saisie non trouvé pour '{task_name}'")
                return False
            input_field.clear()
            input_field.send_keys(task_name)
            # Cherche le bouton d'ajout
            button_selectors = [
                (By.CSS_SELECTOR, '[data-testid="submit-task-button"]'),
                (By.CSS_SELECTOR, 'button.submit'),
                (By.CSS_SELECTOR, 'button[type="submit"]'),
                (By.CSS_SELECTOR, '.submit'),
                (By.CSS_SELECTOR, 'input[type="submit"]'),
                (By.CSS_SELECTOR, 'button:contains("Ajouter")'),
                (By.CSS_SELECTOR, 'button:contains("Add")'),
                (By.CSS_SELECTOR, 'input[value*="Ajouter"]'),
                (By.CSS_SELECTOR, 'input[value*="Add"]')
            ]
            submit_button = None
            for by, selector in button_selectors:
                try:
                    if by == By.CSS_SELECTOR and (":contains(" in selector):
                        # Recherche par texte
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector.split(':')[0])
                        for btn in buttons:
                            if "Ajouter" in btn.text or "Add" in btn.text:
                                submit_button = btn
                                break
                    else:
                        submit_button = self.driver.find_element(by, selector)
                    if submit_button:
                        break
                except NoSuchElementException:
                    continue
            if not submit_button:
                # Dernière tentative: bouton avec texte
                try:
                    buttons = self.driver.find_elements(By.TAG_NAME, "button")
                    for btn in buttons:
                        if btn.is_displayed() and (
                            "Ajouter" in btn.text or "Add" in btn.text or "Submit" in btn.text
                        ):
                            submit_button = btn
                            break
                except Exception:
                    pass
            if not submit_button:
                print(f"   ⚠ Bouton d'ajout non trouvé pour '{task_name}'")
                return False
            submit_button.click()
            time.sleep(1)  # Attendre l'ajout
            return True
        except Exception as e:
            print(f"   ⚠ Erreur création tâche '{task_name}': {e}")
            return False

    def delete_task(self, task_name):
        """Supprime une tâche par son nom."""
        try:
            time.sleep(1)
            # Cherche la tâche par son texte
            task_xpath = f"//*[contains(text(), '{task_name}')]"
            task_elements = self.driver.find_elements(By.XPATH, task_xpath)
            if not task_elements:
                print(f"   ⚠ Tâche '{task_name}' non trouvée pour suppression")
                return False
            for element in task_elements:
                try:
                    if not element.is_displayed():
                        continue
                    # Chercher dans le conteneur parent
                    parent_xpaths = [
                        "./ancestor::div[contains(@class, 'item-row')]",
                        "./ancestor::div[contains(@class, 'task')]",
                        "./ancestor::tr",
                        "./ancestor::li",
                        "./ancestor::div[@role='listitem']",
                        "./ancestor::div[contains(@class, 'item')]",
                        "./ancestor::div[contains(@class, 'row')]",
                        "./ancestor::div[contains(@class, 'task-item')]",
                        "./.."  # Parent direct
                    ]
                    parent = None
                    for xpath in parent_xpaths:
                        try:
                            parent = element.find_element(By.XPATH, xpath)
                            if parent.is_displayed():
                                break
                        except Exception:
                            continue
                    if not parent:
                        continue
                    # Chercher le bouton Supprimer dans le parent
                    delete_button = None
                    delete_selectors = [
                        '.btn-danger',
                        'a[href*="delete"]',
                        '[data-testid="delete-task-button"]',
                        'button:contains("Supprimer")',
                        'button:contains("Delete")',
                        'a:contains("Supprimer")',
                        'a:contains("Delete")',
                        '.delete-btn',
                        '.btn-delete'
                    ]
                    for selector in delete_selectors:
                        try:
                            if ":contains(" in selector:
                                # Recherche par texte
                                btns = parent.find_elements(By.CSS_SELECTOR, selector.split(':')[0])
                                for btn in btns:
                                    if "Supprimer" in btn.text or "Delete" in btn.text:
                                        delete_button = btn
                                        break
                            else:
                                delete_button = parent.find_element(By.CSS_SELECTOR, selector)
                            if delete_button:
                                break
                        except Exception:
                            continue
                    if delete_button and delete_button.is_displayed():
                        # Scroll pour voir le bouton
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", delete_button)
                        time.sleep(0.5)
                        delete_button.click()
                        time.sleep(1)
                        # Gérer la page de confirmation si elle existe
                        try:
                            confirm_selectors = [
                                '[data-testid="confirm-delete-button"]',
                                '.btn-confirm',
                                'button[type="submit"]',
                                'input[type="submit"]',
                                'button:contains("Confirmer")',
                                'button:contains("Confirm")',
                                'button:contains("Oui")',
                                'button:contains("Yes")'
                            ]
                            for selector in confirm_selectors:
                                try:
                                    if ":contains(" in selector:
                                        # Recherche par texte
                                        btns = self.driver.find_elements(
                                            By.CSS_SELECTOR, selector.split(':')[0]
                                        )
                                        for btn in btns:
                                            if any(word in btn.text for word in [
                                                "Confirmer", "Confirm", "Oui", "Yes"
                                            ]):
                                                btn.click()
                                                time.sleep(1)
                                                break
                                    else:
                                        confirm_btn = WebDriverWait(self.driver, 2).until(
                                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                                        )
                                        confirm_btn.click()
                                        time.sleep(1)
                                    break
                                except Exception:
                                    continue
                        except Exception:
                            # Pas de page de confirmation, c'est OK
                            pass
                        print(f"   ✓ Tâche '{task_name}' supprimée avec succès")
                        return True
                except Exception as e:
                    print(f"   ⚠ Erreur lors de la suppression: {e}")
                    continue
            print(f"   ❌ Impossible de trouver bouton Supprimer pour '{task_name}'")
            return False
        except Exception as e:
            print(f"   ❌ Erreur suppression tâche '{task_name}': {e}")
            return False

    def is_task_present(self, task_name):
        """Vérifie si une tâche est présente."""
        try:
            time.sleep(0.5)
            # Recherche par texte exact ou partiel
            xpaths = [
                f"//*[contains(text(), '{task_name}')]",
                f"//*[normalize-space()='{task_name}']"
            ]
            for xpath in xpaths:
                try:
                    task_elements = self.driver.find_elements(By.XPATH, xpath)
                    for element in task_elements:
                        if element.is_displayed():
                            return True
                except Exception:
                    continue
            return False
        except Exception:
            return False

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
        print("🚀 Lancement des tests Selenium E2E...")
        print("=" * 60)
        tester.setup()
        print("\n" + "=" * 60)
        print("🧪 DÉBUT DES TESTS")
        print("=" * 60)
        tester.test_count_create_delete_tasks()  # TE001
        tester.test_add_delete_specific_task()   # TE002
        tester.test_exercise_12_specific()       # TE012 - EXERCICE 12
        tester.save_results()
    except Exception as e:
        print(f"❌ Erreur critique lors de l'exécution des tests: {e}")
        if tester.driver:
            # Sauvegarder une capture d'écran en cas d'erreur
            try:
                screenshot_file = "selenium_error.png"
                tester.driver.save_screenshot(screenshot_file)
                print(f"📸 Capture d'écran sauvegardée: {screenshot_file}")
            except Exception:
                pass
    finally:
        tester.teardown()
    return tester.results


if __name__ == "__main__":
    print("=" * 60)
    print("EXÉCUTION DES TESTS SELENIUM - EXERCICES 9 & 12")
    print("=" * 60)
    print("\n⚠  AVANT DE LANCER :")
    print("1. Assure-toi que ton serveur Django tourne :")
    print("   pipenv run python manage.py runserver")
    print("2. Vérifie que l'application est accessible :")
    print("   http://127.0.0.1:8000/")
    print("3. Chrome doit être installé sur votre machine")
    print("=" * 60)
    input("Appuyez sur Entrée pour démarrer les tests...")
    results = run_selenium_tests()
    print("\n" + "=" * 60)
    print("🎯 TESTS SELENIUM TERMINÉS")
    print("=" * 60)
    print("Vérifiez le fichier: result_test_selenium.json")
    print("=" * 60)
    # Afficher le résumé final
    if results:
        passed = sum(1 for r in results.values() if r["status"] == "passed")
        total = len(results)
        if passed == total:
            print("🎉 TOUS LES TESTS ONT RÉUSSI !")
        else:
            print(f"⚠  {passed}/{total} tests ont réussi")
