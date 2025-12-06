#!/usr/bin/env python3
"""
Script de rapport de tests - Exercice 11 et 18
Modifié pour prendre en compte:
- Tests "auto-selenium" (Exercice 11)
- Tests d'accessibilité "auto-accessibility" (Exercice 18)
"""

import yaml
import json
import os
import subprocess
import sys
import time


def load_test_list():
    """Charge la liste des tests depuis YAML."""
    try:
        with open('test_list.yaml', 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            if isinstance(data, dict):
                return data.get('tests', {})
            else:
                print("❌ Erreur: Structure YAML incorrecte")
                return {}
    except FileNotFoundError:
        print("❌ test_list.yaml non trouvé")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Erreur YAML: {e}")
        return {}


def load_django_results():
    """Charge les résultats des tests Django depuis JSON avec gestion d'encodage."""
    json_file = 'result_test_auto.json'

    if not os.path.exists(json_file):
        print("⚠️  result_test_auto.json non trouvé")
        return {}

    # Essayer différents encodages
    encodings_to_try = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']

    for encoding in encodings_to_try:
        try:
            with open(json_file, 'r', encoding=encoding) as f:
                content = f.read()
                data = json.loads(content)
                print(f"✅ Fichier JSON chargé avec succès (encodage: {encoding})")
                return data
        except UnicodeDecodeError:
            continue
        except json.JSONDecodeError:
            continue

    print("❌ Impossible de lire le fichier JSON avec les encodages disponibles")
    return {}


def load_selenium_results():
    """Charge les résultats des tests Selenium depuis JSON."""
    try:
        with open('result_test_selenium.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            tests = data.get('tests', {})
            count = len(tests)

            if 'summary' in data:
                passed = data['summary'].get('passed', 0)
                failed = data['summary'].get('failed', 0)
                msg = (f"✅ Fichier result_test_selenium.json chargé "
                       f"({count} tests, {passed}✅ {failed}❌)")
                print(msg)
            else:
                msg = f"✅ Fichier result_test_selenium.json chargé ({count} tests Selenium)"
                print(msg)

            return tests
    except FileNotFoundError:
        msg = "⚠️  result_test_selenium.json non trouvé (tests Selenium non disponibles)"
        print(msg)
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur JSON dans result_test_selenium.json: {e}")
        return {}


def create_test_task_for_accessibility():
    """Crée une tâche de test via Selenium pour obtenir un ID valide."""
    print("\n🛠️  Création d'une tâche de test pour obtenir un ID...")

    try:
        # Importer Selenium
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options

        # Configuration Chrome en mode headless
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        try:
            from webdriver_manager.chrome import ChromeDriverManager
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception:
            # Fallback si webdriver_manager n'est pas disponible
            driver = webdriver.Chrome(options=chrome_options)

        driver.implicitly_wait(5)

        try:
            # Aller sur la page d'accueil
            driver.get("http://127.0.0.1:8000/")
            time.sleep(2)

            # Créer une nouvelle tâche
            task_name = f"Test Accessibilité {int(time.time())}"

            # Trouver le champ de saisie
            input_selectors = [
                (By.NAME, "title"),
                (By.ID, "id_title"),
                (By.CSS_SELECTOR, 'input[type="text"]'),
                (By.CSS_SELECTOR, 'textarea[name="title"]'),
                (By.CSS_SELECTOR, 'input[name="title"]'),
            ]

            input_field = None
            for by, selector in input_selectors:
                try:
                    input_field = driver.find_element(by, selector)
                    if input_field.is_displayed():
                        break
                except Exception:
                    continue

            if not input_field:
                # Dernière tentative
                try:
                    inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"], textarea')
                    for inp in inputs:
                        if inp.is_displayed():
                            input_field = inp
                            break
                except Exception:
                    pass

            if not input_field:
                print("❌ Impossible de trouver le champ de saisie")
                driver.quit()
                return None

            # Remplir le champ
            input_field.clear()
            input_field.send_keys(task_name)
            time.sleep(1)

            # Trouver le bouton d'ajout
            submit_button = None
            button_texts = ['Ajouter', 'Add', 'Submit', 'Créer', 'Create', 'Save', 'Valider']

            for text in button_texts:
                try:
                    buttons = driver.find_elements(
                        By.XPATH, f"//button[contains(text(), '{text}')]"
                    )
                    for btn in buttons:
                        if btn.is_displayed():
                            submit_button = btn
                            break
                    if submit_button:
                        break
                except Exception:
                    continue

            if not submit_button:
                # Chercher par type
                try:
                    submit_button = driver.find_element(
                        By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]'
                    )
                except Exception:
                    pass

            if not submit_button:
                # Premier bouton visible
                try:
                    buttons = driver.find_elements(By.TAG_NAME, 'button')
                    for btn in buttons:
                        if btn.is_displayed() and btn.is_enabled():
                            submit_button = btn
                            break
                except Exception:
                    pass

            if not submit_button:
                print("❌ Impossible de trouver le bouton d'ajout")
                driver.quit()
                return None

            # Cliquer pour créer la tâche
            submit_button.click()
            time.sleep(2)

            # Récupérer l'ID de la tâche créée
            # Chercher des liens ou éléments contenant l'ID
            page_source = driver.page_source

            # Chercher des patterns d'ID dans les URLs
            import re
            id_patterns = [
                r'/update_task/(\d+)/',
                r'/delete_task/(\d+)/',
                r'/task/(\d+)/',
                r'/tasks/(\d+)/',
                r'/edit/(\d+)/',
            ]

            task_id = None
            for pattern in id_patterns:
                matches = re.findall(pattern, page_source)
                if matches:
                    # Prendre le plus grand ID (le plus récent)
                    ids = [int(match) for match in matches]
                    if ids:
                        task_id = max(ids)
                        break

            if task_id:
                print(f"✅ Tâche créée avec ID: {task_id}")
            else:
                print("⚠️  Impossible de trouver l'ID, utilisation de l'ID 1 par défaut")
                task_id = 1

            driver.quit()
            return task_id

        except Exception as e:
            print(f"❌ Erreur lors de la création de la tâche: {e}")
            driver.quit()
            return None

    except ImportError as e:
        print(f"⚠️  Selenium non disponible: {e}")
        print("💡 Installation: pipenv install selenium webdriver-manager")
        return None
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return None


def run_simple_accessibility_check(url):
    """Vérifie l'accessibilité basique d'une URL."""
    try:
        # Essayer d'importer requests
        try:
            import requests
        except ImportError:
            return {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': ['requests non installé. Installez: pipenv install requests'],
                'warnings': []
            }

        # Vérifier d'abord si le serveur est accessible
        try:
            print(f"    🔍 Test de {url}...")
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                return {
                    'url': url,
                    'status': 'failed',
                    'score': 0,
                    'errors_count': 1,
                    'warnings_count': 0,
                    'errors': [f'HTTP {response.status_code} - Serveur en erreur'],
                    'warnings': []
                }
        except requests.exceptions.ConnectionError:
            return {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': ['❌ Serveur inaccessible - Lancez: pipenv run python manage.py runserver'],
                'warnings': []
            }
        except requests.exceptions.Timeout:
            return {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': ['⏱️  Timeout - Serveur trop lent'],
                'warnings': []
            }

        # Vérifications de base sur le HTML
        html = response.text

        checks = {
            'has_title': '<title>' in html,
            'has_lang': 'lang=' in html.lower() or 'xml:lang=' in html.lower(),
            'has_headings': '<h1' in html or '<h2' in html,
            'has_alt': 'alt=' in html.lower(),
            'has_labels': 'label' in html.lower(),
            'has_buttons': 'button' in html.lower() or 'type="submit"' in html.lower(),
            'has_forms': '<form' in html.lower(),
            'has_aria': 'aria-' in html.lower(),
            'has_navigation': 'nav' in html.lower() or 'role="navigation"' in html.lower(),
            'has_main': 'main' in html.lower() or 'role="main"' in html.lower()
        }

        # Calcul du score
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        score = int((passed_checks / total_checks) * 100)

        # Détecter les erreurs potentielles
        errors = []
        warnings = []

        if not checks['has_title']:
            errors.append("❌ Pas de titre de page (<title>)")
        if not checks['has_lang']:
            errors.append("❌ Attribut de langue manquant (lang='fr')")
        if not checks['has_alt'] and '<img' in html.lower():
            warnings.append("⚠️  Images sans texte alternatif détectées")
        if not checks['has_labels'] and checks['has_forms']:
            warnings.append("⚠️  Formulaires sans labels détectés")
        if not checks['has_aria']:
            warnings.append("ℹ️  Pas d'attributs ARIA détectés")

        status = 'passed' if score >= 80 and len(errors) == 0 else 'failed'

        return {
            'url': url,
            'status': status,
            'score': score,
            'errors_count': len(errors),
            'warnings_count': len(warnings),
            'errors': errors,
            'warnings': warnings,
            'checks': checks
        }

    except Exception as e:
        return {
            'url': url,
            'status': 'failed',
            'score': 0,
            'errors_count': 1,
            'warnings_count': 0,
            'errors': [f'Erreur: {str(e)}'],
            'warnings': []
        }


def run_accessibility_tests():
    """EXERCICE 18: Exécute les tests d'accessibilité."""
    print("\n" + "=" * 60)
    print("♿ EXÉCUTION DES TESTS D'ACCESSIBILITÉ (EXERCICE 18)")
    print("=" * 60)

    # Créer d'abord une tâche pour avoir un ID valide
    task_id = create_test_task_for_accessibility()

    # URLs avec ID dynamique
    if task_id:
        urls_to_test = [
            "http://127.0.0.1:8000/",  # Page d'accueil
            f"http://127.0.0.1:8000/update_task/{task_id}/",  # Modification avec ID
            f"http://127.0.0.1:8000/delete_task/{task_id}/",  # Suppression avec ID
        ]
        print(f"\n📋 3 pages à tester avec ID de tâche: {task_id}")
    else:
        # Si on ne peut pas créer de tâche, tester seulement l'accueil
        urls_to_test = [
            "http://127.0.0.1:8000/",  # Page d'accueil seulement
        ]
        print("\n📋 1 page à tester (accueil seulement)")

    for i, url in enumerate(urls_to_test):
        print(f"   {i + 1}. {url}")

    # Vérifier si Pa11y est disponible
    pa11y_available = False
    try:
        if sys.platform == "win32":
            result = subprocess.run(["where", "pa11y"], capture_output=True, text=True)
        else:
            result = subprocess.run(["which", "pa11y"], capture_output=True, text=True)
        pa11y_available = result.returncode == 0
    except Exception:
        pa11y_available = False

    if pa11y_available:
        print("\n✅ Pa11y détecté, utilisation des tests complets")
        return run_pa11y_tests(urls_to_test)
    else:
        print("\n⚠️  Pa11y non disponible, utilisation des tests simplifiés")
        print("💡 Pour les tests complets: npm install -g pa11y")
        return run_simple_accessibility_tests(urls_to_test)


def run_pa11y_tests(urls_to_test):
    """Exécute les tests avec Pa11y."""
    results = {}
    total_score = 0
    tests_count = 0

    for i, url in enumerate(urls_to_test):
        test_id = f"AC{i + 1:03d}"
        print(f"\n  🧪 Test {test_id}: {url}")

        try:
            # Vérifier si la page est accessible
            try:
                import requests
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    results[test_id] = {
                        'url': url,
                        'status': 'failed',
                        'score': 0,
                        'errors_count': 1,
                        'warnings_count': 0,
                        'errors': [f'HTTP {response.status_code}'],
                        'warnings': []
                    }
                    print(f"    ❌ Page inaccessible (HTTP {response.status_code})")
                    continue
            except ImportError:
                pass  # Continue même si requests n'est pas installé

            # Exécuter Pa11y
            cmd = ["pa11y", "--reporter", "json", url]

            # Ajuster pour Windows
            if sys.platform == "win32":
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    shell=True
                )
            else:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            if result.returncode == 0 or result.stdout:
                try:
                    pa11y_result = json.loads(result.stdout)

                    # Extraire les erreurs et warnings selon la structure de Pa11y
                    errors = []
                    warnings = []

                    if isinstance(pa11y_result, list):
                        # Format array
                        for issue in pa11y_result:
                            if isinstance(issue, dict):
                                if issue.get('type') == 'error':
                                    errors.append(issue)
                                else:
                                    warnings.append(issue)
                    elif isinstance(pa11y_result, dict):
                        # Format object avec issues
                        if 'issues' in pa11y_result:
                            if isinstance(pa11y_result['issues'], list):
                                for issue in pa11y_result['issues']:
                                    if isinstance(issue, dict):
                                        if issue.get('type') == 'error':
                                            errors.append(issue)
                                        else:
                                            warnings.append(issue)
                            elif isinstance(pa11y_result['issues'], dict):
                                errors = pa11y_result['issues'].get('errors', [])
                                warnings = pa11y_result['issues'].get('warnings', [])

                    score = 100 if not errors else max(0, 100 - len(errors) * 10)
                    status = 'passed' if score >= 90 else 'failed'

                    results[test_id] = {
                        'url': url,
                        'status': status,
                        'score': score,
                        'errors_count': len(errors),
                        'warnings_count': len(warnings),
                        'errors': errors[:3],
                        'warnings': warnings[:3]
                    }

                    total_score += score
                    tests_count += 1

                    status_icon = "✅" if status == 'passed' else "❌"
                    msg = (f"    {status_icon} Score: {score}% "
                           f"({len(errors)} erreurs, {len(warnings)} warnings)")
                    print(msg)

                except json.JSONDecodeError:
                    # Pa11y a peut-être retourné du texte au lieu du JSON
                    results[test_id] = {
                        'url': url,
                        'status': 'failed',
                        'score': 0,
                        'errors_count': 1,
                        'warnings_count': 0,
                        'errors': ['Erreur de parsing JSON Pa11y'],
                        'warnings': []
                    }
                    print("    ❌ Erreur de parsing JSON")
                    print(f"    Sortie: {result.stdout[:100]}...")
            else:
                results[test_id] = {
                    'url': url,
                    'status': 'failed',
                    'score': 0,
                    'errors_count': 1,
                    'warnings_count': 0,
                    'errors': ['Échec d\'exécution Pa11y'],
                    'warnings': []
                }
                print("    ❌ Échec d'exécution")

        except subprocess.TimeoutExpired:
            results[test_id] = {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': ['Timeout Pa11y'],
                'warnings': []
            }
            print("    ⏱️  Timeout")
        except Exception as e:
            results[test_id] = {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': [str(e)],
                'warnings': []
            }
            print(f"    ❌ Erreur: {e}")

    if tests_count > 0:
        avg_score = total_score / tests_count
        print(f"\n📊 RÉSUMÉ ACCESSIBILITÉ: {tests_count} pages testées, score moyen: {avg_score:.1f}%")
    else:
        print("\n📊 RÉSUMÉ ACCESSIBILITÉ: Aucune page testée avec succès")

    return results


def run_simple_accessibility_tests(urls_to_test):
    """Exécute les tests d'accessibilité simplifiés."""
    results = {}
    total_score = 0
    tests_count = 0

    for i, url in enumerate(urls_to_test):
        test_id = f"AC{i + 1:03d}"
        print(f"\n  🧪 Test {test_id}: {url}")

        result = run_simple_accessibility_check(url)
        results[test_id] = result

        if result['score'] > 0:
            total_score += result['score']
            tests_count += 1

        status_icon = "✅" if result['status'] == 'passed' else "❌"
        msg = (f"    {status_icon} Score: {result['score']}% "
               f"({result['errors_count']} erreurs, {result['warnings_count']} warnings)")
        print(msg)

        # Afficher les erreurs si présentes
        if result['errors_count'] > 0:
            for error in result['errors']:
                print(f"        {error}")

    if tests_count > 0:
        avg_score = total_score / tests_count
        print(f"\n📊 RÉSUMÉ ACCESSIBILITÉ: {tests_count} pages testées, score moyen: {avg_score:.1f}%")
    else:
        print("\n📊 RÉSUMÉ ACCESSIBILITÉ: Aucune page testée avec succès")

    return results


def get_accessibility_results():
    """Récupère les résultats d'accessibilité."""
    # Vérifier s'il y a un cache récent
    cache_file = '.pa11y_cache.json'
    cache_max_age = 300  # 5 minutes

    if os.path.exists(cache_file):
        import time
        file_age = time.time() - os.path.getmtime(cache_file)

        if file_age < cache_max_age:
            print("♿ Utilisation du cache des tests d'accessibilité...")
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass  # Si le cache est corrompu, on refait les tests

    # Exécuter les tests
    results = run_accessibility_tests()

    # Sauvegarder en cache
    try:
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception:
        pass

    return results


def get_test_status(test_id, test_type, django_results, selenium_results, accessibility_results):
    """Détermine le statut d'un test."""
    if test_type == 'manuel':
        return "💬Manual test needed", "👤"

    elif test_type == 'auto-unittest':
        result = django_results.get(test_id)
        if result:
            status = result.get('status', 'unknown')
            if status == 'passed':
                return "✔Passed", "✅"
            elif status == 'failed':
                return "✘Failed", "❌"
            else:
                return "💬Unknown", "❓"
        return "💬Not found", "❓"

    elif test_type == 'auto-selenium':
        result = selenium_results.get(test_id)
        if result:
            status = result.get('status', 'unknown')
            if status == 'passed':
                return "✔Passed", "✅"
            elif status == 'failed':
                return "✘Failed", "❌"
            else:
                return "💬Unknown", "❓"
        return "💬Not found", "❓"

    elif test_type == 'auto-accessibility':
        result = accessibility_results.get(test_id)
        if result:
            status = result.get('status', 'unknown')
            if status == 'passed':
                return "✔Passed", "✅"
            elif status == 'failed':
                return "✘Failed", "❌"
            else:
                return "💬Unknown", "❓"
        return "💬Not found", "❓"

    return "💬Type inconnu", "❓"


def main():
    """Génère le rapport de tests avec support Selenium et Accessibilité."""
    print("📊 GÉNÉRATION DU RAPPORT DE TESTS AVANCÉ")
    print("=" * 60)
    print("Lecture des tests auto via result_test_auto.json…")
    print("Lecture des tests Selenium via result_test_selenium.json…")

    tests = load_test_list()
    django_results = load_django_results()
    selenium_results = load_selenium_results()

    print()

    # EXERCICE 18: Récupérer les résultats d'accessibilité
    accessibility_results = get_accessibility_results()

    print("\n✅ TOUS LES TESTS ONT ÉTÉ CHARGÉS")

    # Initialise les compteurs
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'not_found': 0,
        'manual': 0,
        'selenium_passed': 0,
        'selenium_failed': 0,
        'selenium_not_found': 0,
        'accessibility_passed': 0,
        'accessibility_failed': 0,
        'accessibility_not_found': 0,
        'accessibility_score': 0,
        'accessibility_tests_executed': len(accessibility_results)
    }

    # ================ RAPPORT VISUEL ================
    print("\n" + "=" * 70)
    print("RAPPORT DÉTAILLÉ DES TESTS (Django + Selenium + Accessibilité)")
    print("=" * 70)

    # Vérifier si tests est valide
    if not isinstance(tests, dict):
        print("❌ Erreur: 'tests' n'est pas un dictionnaire valide")
        print(f"   Type obtenu: {type(tests)}")
        print(f"   Valeur: {tests}")
        return stats

    # Affiche chaque test
    for test_id in sorted(tests.keys()):
        stats['total'] += 1

        # CORRECTION : Vérifier si test_info est un dictionnaire
        test_info = tests[test_id]
        if isinstance(test_info, dict):
            test_type = test_info.get('type', 'unknown')
            test_desc = test_info.get('description', '')[:40]
        elif isinstance(test_info, str):
            # Si c'est une string, c'est peut-être une description
            test_type = 'unknown'
            test_desc = test_info[:40]
        else:
            # Type inconnu
            test_type = 'unknown'
            test_desc = str(test_info)[:40]

        if len(test_desc) > 40:
            test_desc = test_desc[:37] + "..."

        # Utilisation de la fonction améliorée
        status, icon = get_test_status(
            test_id, test_type,
            django_results, selenium_results, accessibility_results
        )

        # Mettre à jour les statistiques
        if status == "✔Passed":
            stats['passed'] += 1
            if test_type == 'auto-selenium':
                stats['selenium_passed'] += 1
            elif test_type == 'auto-accessibility':
                stats['accessibility_passed'] += 1
                if test_id in accessibility_results:
                    stats['accessibility_score'] += accessibility_results[test_id].get('score', 100)

        elif status == "✘Failed":
            stats['failed'] += 1
            if test_type == 'auto-selenium':
                stats['selenium_failed'] += 1
            elif test_type == 'auto-accessibility':
                stats['accessibility_failed'] += 1
                if test_id in accessibility_results:
                    stats['accessibility_score'] += accessibility_results[test_id].get('score', 0)

        elif status == "💬Not found":
            stats['not_found'] += 1
            if test_type == 'auto-selenium':
                stats['selenium_not_found'] += 1
            elif test_type == 'auto-accessibility':
                stats['accessibility_not_found'] += 1
        elif status == "💬Manual test needed":
            stats['manual'] += 1
        elif status == "💬Unknown":
            stats['not_found'] += 1

        # Afficher la ligne du test
        print(f"{icon} {test_id:6} | {test_type:20} | {status:20} | {test_desc}")

    print("=" * 70)

    # ================ STATISTIQUES ================
    print("\n📊 STATISTIQUES COMPLÈTES")
    print("=" * 50)

    if stats['total'] > 0:
        # Pourcentages généraux
        passed_pct = (stats['passed'] / stats['total']) * 100
        failed_pct = (stats['failed'] / stats['total']) * 100
        not_found_pct = (stats['not_found'] / stats['total']) * 100
        manual_pct = (stats['manual'] / stats['total']) * 100

        print("📈 VUE D'ENSEMBLE")
        print(f"   Nombre total de tests: {stats['total']}")
        print(f"   ✔ Tests réussis: {stats['passed']} ({passed_pct:.1f}%)")
        print(f"   ✘ Tests échoués: {stats['failed']} ({failed_pct:.1f}%)")
        print(f"   💬 Tests non trouvés: {stats['not_found']} ({not_found_pct:.1f}%)")
        print(f"   👤 Tests manuels: {stats['manual']} ({manual_pct:.1f}%)")

        total_ok = stats['passed'] + stats['manual']
        total_ok_pct = passed_pct + manual_pct
        print(f"   ✅ Total validé: {total_ok} ({total_ok_pct:.1f}%)")

        # ================ STATISTIQUES PAR TYPE ================
        print("\n🔧 TESTS TECHNIQUES")

        # Django Unit Tests - CORRIGÉ ICI
        django_total = sum(1 for t in tests.values()
                           if isinstance(t, dict) and t.get('type') == 'auto-unittest')
        if django_total > 0:
            django_passed = sum(
                1 for tid in tests.keys()
                if isinstance(tests[tid], dict)
                and tests[tid].get('type') == 'auto-unittest'
                and get_test_status(
                    tid, 'auto-unittest', django_results,
                    selenium_results, accessibility_results
                )[0] == "✔Passed"
            )
            django_pct = (django_passed / django_total) * 100 if django_total > 0 else 0
            msg = f"   🐍 Django Unit Tests: {django_passed}/{django_total} ({django_pct:.1f}%)"
            print(msg)

        # Selenium
        selenium_total = (
            stats['selenium_passed']
            + stats['selenium_failed']
            + stats['selenium_not_found']
        )
        if selenium_total > 0:
            selenium_passed_pct = (stats['selenium_passed'] / selenium_total) * 100 if selenium_total > 0 else 0
            msg = (
                f"   🌐 Selenium E2E: {stats['selenium_passed']}/{selenium_total} "
                f"({selenium_passed_pct:.1f}%)"
            )
            print(msg)

        # ================ EXERCICE 18 : ACCESSIBILITÉ ================
        print("\n♿ ACCESSIBILITÉ (Exercice 18)")

        accessibility_total = (
            stats['accessibility_passed']
            + stats['accessibility_failed']
            + stats['accessibility_not_found']
        )

        if accessibility_total > 0:
            if stats['accessibility_passed'] + stats['accessibility_failed'] > 0:
                avg_score = (
                    stats['accessibility_score']
                    / (stats['accessibility_passed'] + stats['accessibility_failed'])
                )
            else:
                avg_score = 0

            accessibility_passed_pct = (stats['accessibility_passed'] / accessibility_total) * 100 if accessibility_total > 0 else 0

            print(f"   Pages testées: {stats['accessibility_tests_executed']}")
            print(f"   Tests définis: {accessibility_total}")
            msg = (
                f"   ✅ Tests réussis: {stats['accessibility_passed']}/{accessibility_total} "
                f"({accessibility_passed_pct:.1f}%)"
            )
            print(msg)
            print(f"   📊 Score moyen: {avg_score:.1f}%")

            # Évaluation de la conformité
            if avg_score >= 95:
                print("   🏆 Conformité WGAC 2.1 Niveau A: ✅ EXCELLENT")
            elif avg_score >= 85:
                print("   👍 Conformité WGAC 2.1 Niveau A: ✅ BON")
            elif avg_score >= 75:
                print("   ⚠️  Conformité WGAC 2.1 Niveau A: MOYEN")
            else:
                print("   ❗ Conformité WGAC 2.1 Niveau A: À AMÉLIORER")

            # Détails des tests exécutés
            if accessibility_results:
                print("\n   📋 DÉTAIL DES TESTS EXÉCUTÉS:")
                for test_id, result in accessibility_results.items():
                    score = result.get('score', 0)
                    errors = result.get('errors_count', 0)
                    warnings = result.get('warnings_count', 0)
                    status_icon = "✅" if result.get('status') == 'passed' else "❌"
                    url = result.get('url', 'N/A')
                    print(f"     {status_icon} {test_id}: {url}")
                    print(f"        Score: {score}% | Erreurs: {errors} | Warnings: {warnings}")

                    # Afficher les premières erreurs si présentes
                    if errors > 0 and 'errors' in result:
                        for error in result['errors'][:2]:
                            if isinstance(error, dict):
                                error_msg = error.get('message', str(error))
                            else:
                                error_msg = str(error)
                            print(f"        ❗ {error_msg[:60]}...")
        else:
            print("   ⚠️  Aucun test d'accessibilité défini dans test_list.yaml")
            print("   💡 Conseil: Ajoutez des tests avec type: 'auto-accessibility'")

        # ================ RÉCAPITULATIF FINAL ================
        print("\n🎯 RÉCAPITULATIF FINAL")
        print("=" * 50)

        categories = [
            ("Django Unit Tests", 'auto-unittest'),
            ("Selenium E2E", 'auto-selenium'),
            ("Accessibilité", 'auto-accessibility'),
            ("Tests Manuels", 'manuel')
        ]

        for name, type_key in categories:
            count = sum(1 for t in tests.values()
                        if isinstance(t, dict) and t.get('type') == type_key)
            if count > 0:
                passed = 0
                for tid in tests.keys():
                    if isinstance(tests[tid], dict) and tests[tid].get('type') == type_key:
                        status, _ = get_test_status(tid, type_key, django_results,
                                                    selenium_results, accessibility_results)
                        if status == "✔Passed":
                            passed += 1

                pct = (passed / count) * 100 if count > 0 else 0
                icon = "✅" if pct >= 90 else "⚠️" if pct >= 70 else "❌"
                msg = f"{icon} {name:25}: {passed:3}/{count:3} ({pct:5.1f}%)"
                print(msg)

    else:
        print("❌ Aucun test trouvé dans test_list.yaml!")

    # ================ VÉRIFICATION EXERCICE 18 ================
    print("\n" + "=" * 60)
    print("VÉRIFICATION EXERCICE 18 - Tests d'accessibilité")
    print("=" * 60)

    # Chercher les tests d'accessibilité dans test_list.yaml
    accessibility_tests = []
    for tid, tinfo in tests.items():
        if isinstance(tinfo, dict) and tinfo.get('type') == 'auto-accessibility':
            accessibility_tests.append((tid, tinfo))
        elif isinstance(tinfo, str) and tid.startswith('AC'):
            accessibility_tests.append((tid, {'description': tinfo, 'type': 'auto-accessibility'}))

    if accessibility_tests:
        print(f"✅ TESTS D'ACCESSIBILITÉ DÉTECTÉS: {len(accessibility_tests)}")
        print("\nDétails des tests d'accessibilité dans test_list.yaml:")

        for test_id, test_info in accessibility_tests:
            if isinstance(test_info, dict):
                desc = test_info.get('description', 'Pas de description')
                expected_url = test_info.get('url', 'URL non spécifiée')
            else:
                desc = str(test_info)
                expected_url = 'URL non spécifiée'

            print(f"\n  📝 {test_id}: {desc}")
            print(f"     URL attendue: {expected_url}")

            # Vérifier si ce test a été exécuté
            if test_id in accessibility_results:
                result = accessibility_results[test_id]
                actual_url = result.get('url', 'N/A')
                score = result.get('score', 0)
                errors = result.get('errors_count', 0)

                msg = f"     ✅ EXÉCUTÉ: Score {score}%, {errors} erreur(s)"
                print(msg)
                print(f"     URL testée: {actual_url}")

                if errors > 0 and 'errors' in result:
                    print("     ❌ Problèmes détectés:")
                    for error in result.get('errors', [])[:2]:
                        if isinstance(error, dict):
                            context = error.get('context', '')
                            selector = error.get('selector', '')
                            print(f"        - {context[:50]}... [selector: {selector}]")
                        else:
                            print(f"        - {str(error)[:60]}...")
            else:
                msg = "     ⚠️  NON EXÉCUTÉ: Aucun résultat d'accessibilité pour ce test"
                print(msg)
                msg = f"     Vérifiez que l'URL {expected_url} est accessible"
                print(msg)
    else:
        print("⚠️  Aucun test 'auto-accessibility' trouvé dans test_list.yaml")
        print("\n💡 POUR AJOUTER DES TESTS D'ACCESSIBILITÉ:")
        print("1. Ajoutez dans test_list.yaml:")
        print("   ACXXX:")
        print("     type: auto-accessibility")
        print("     description: \"Test d'accessibilité de la page X\"")
        print("     url: \"http://127.0.0.1:8000/\"")
        print("\n2. Les tests seront automatiquement exécutés")

    return stats


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
