#!/usr/bin/env python3
"""
Script de rapport de tests - Exercice 11 et 18
Modifié pour prendre en compte:
- Tests "auto-selenium" (Exercice 11)
- Tests d'accessibilité "auto-accessibility" (Exercice 18)
- Intégration directe de Pa11y
"""

import yaml
import json
import os
import subprocess


def load_test_list():
    """Charge la liste des tests depuis YAML."""
    try:
        with open('test_list.yaml', 'r') as f:
            data = yaml.safe_load(f)
            return data.get('tests', {})
    except FileNotFoundError:
        print("❌ test_list.yaml non trouvé")
        return {}
    except yaml.YAMLError as e:
        print(f"❌ Erreur YAML: {e}")
        return {}


def load_django_results():
    """Charge les résultats des tests Django depuis JSON."""
    try:
        with open('result_test_auto.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  result_test_auto.json non trouvé")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur JSON: {e}")
        return {}


def load_selenium_results():
    """Charge les résultats des tests Selenium depuis JSON."""
    try:
        with open('result_test_selenium.json', 'r') as f:
            data = json.load(f)
            tests = data.get('tests', {})
            count = len(tests)

            if 'summary' in data:
                passed = data['summary'].get('passed', 0)
                failed = data['summary'].get('failed', 0)
                msg = f"✅ Fichier result_test_selenium.json chargé ({count} tests, {passed}✅ {failed}❌)"
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


def run_pa11y_accessibility_tests():
    """
    EXERCICE 18: Exécute les tests d'accessibilité avec Pa11y
    et retourne les résultats directement.
    """
    print("\n♿ EXÉCUTION DES TESTS D'ACCESSIBILITÉ PA11Y...")

    # URLs à tester (ajuster selon ton application)
    urls_to_test = [
        "http://127.0.0.1:8000/",
        "http://127.0.0.1:8000/tasks/",
        "http://127.0.0.1:8000/login/",
        "http://127.0.0.1:8000/register/",
    ]

    results = {}
    total_score = 0
    tests_count = 0

    for i, url in enumerate(urls_to_test):
        test_id = f"AC{i+1:03d}"

        print(f"  Testing {url}...")

        try:
            # Exécute Pa11y en ligne de commande
            # Note: Assure-toi que Pa11y est installé globalement: npm install -g pa11y
            cmd = ["pa11y", "--reporter", "json", url]

            # Exécute la commande avec timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                try:
                    # Parse le résultat JSON
                    pa11y_result = json.loads(result.stdout)

                    # Extraire les informations importantes
                    errors = pa11y_result.get('issues', {}).get('errors', [])
                    warnings = pa11y_result.get('issues', {}).get('warnings', [])

                    # Calculer le score
                    if errors:
                        # Pénalité pour chaque erreur
                        score = max(0, 100 - len(errors) * 10)  # CORRECTION: ajout d'espaces
                        status = 'failed'
                    else:
                        score = 100
                        status = 'passed'

                    results[test_id] = {
                        'url': url,
                        'status': status,
                        'score': score,
                        'errors_count': len(errors),
                        'warnings_count': len(warnings),
                        'errors': errors[:5],  # Limiter à 5 erreurs pour l'affichage
                        'documentTitle': pa11y_result.get('documentTitle', ''),
                        'pageUrl': pa11y_result.get('pageUrl', url)
                    }

                    total_score += score
                    tests_count += 1

                    status_icon = "✅" if status == 'passed' else "❌"
                    msg = f"    {status_icon} {test_id}: {url} - Score: {score}% ({len(errors)} erreurs, {len(warnings)} warnings)"
                    print(msg)

                except json.JSONDecodeError:
                    # Si Pa11y ne retourne pas de JSON valide
                    results[test_id] = {
                        'url': url,
                        'status': 'failed',
                        'score': 0,
                        'errors_count': 1,
                        'warnings_count': 0,
                        'errors': [{'message': 'Invalid JSON response from Pa11y'}],
                        'error': 'JSON decode error'
                    }
                    print(f"    ❌ {test_id}: Erreur de parsing JSON")
            else:
                # Pa11y a échoué
                results[test_id] = {
                    'url': url,
                    'status': 'failed',
                    'score': 0,
                    'errors_count': 1,
                    'warnings_count': 0,
                    'errors': [{'message': f'Pa11y execution failed: {result.stderr[:100]}'}],
                    'error': 'Pa11y execution failed'
                }
                print(f"    ❌ {test_id}: Échec d'exécution de Pa11y")

        except subprocess.TimeoutExpired:
            results[test_id] = {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': [{'message': 'Pa11y timeout after 30 seconds'}],
                'error': 'Timeout'
            }
            print(f"    ⏱️  {test_id}: Timeout")
        except Exception as e:
            results[test_id] = {
                'url': url,
                'status': 'failed',
                'score': 0,
                'errors_count': 1,
                'warnings_count': 0,
                'errors': [{'message': f'Unexpected error: {str(e)}'}],
                'error': 'Unexpected error'
            }
            print(f"    ❌ {test_id}: Erreur inattendue: {e}")

    # Calculer le score moyen
    avg_score = total_score / tests_count if tests_count > 0 else 0

    msg = f"\n📊 RÉSUMÉ ACCESSIBILITÉ: {tests_count} pages testées, score moyen: {avg_score:.1f}%"
    print(msg)

    return results


def get_accessibility_results():
    """Récupère les résultats d'accessibilité (exécute Pa11y ou lit depuis cache)."""

    # Vérifier s'il y a un cache récent
    cache_file = '.pa11y_cache.json'
    cache_max_age = 300  # 5 minutes en secondes

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

    # Exécuter Pa11y
    results = run_pa11y_accessibility_tests()

    # Sauvegarder en cache
    try:
        with open(cache_file, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception:
        pass  # Ignorer les erreurs de cache

    return results


def get_test_status(test_id, test_type, django_results, selenium_results, accessibility_results):
    """Détermine le statut d'un test, y compris auto-selenium et auto-accessibility."""
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
                return "💬Not found", "❓"
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
                return "💬Not found", "❓"
        return "💬Not found", "❓"

    elif test_type == 'auto-accessibility':
        # EXERCICE 18: Vérification spécifique pour les tests d'accessibilité
        result = accessibility_results.get(test_id)
        if result:
            status = result.get('status', 'unknown')
            if status == 'passed':
                return "✔Passed", "✅"
            elif status == 'failed':
                return "✘Failed", "❌"
            else:
                return "💬Not found", "❓"
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

    # EXERCICE 18: Récupérer les résultats d'accessibilité
    accessibility_results = get_accessibility_results()

    print()
    print("✅ TOUS LES TESTS ONT ÉTÉ CHARGÉS")
    print()

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

    # Affiche chaque test
    for test_id in sorted(tests.keys()):
        stats['total'] += 1
        test_info = tests[test_id]
        test_type = test_info.get('type', 'unknown')

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

        # Afficher la ligne du test
        test_desc = test_info.get('description', '')[:40]
        if len(test_desc) > 40:
            test_desc = test_desc[:37] + "..."

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

        # Django Unit Tests
        django_total = sum(1 for t in tests.values() if t.get('type') == 'auto-unittest')
        if django_total > 0:
            django_passed = sum(1 for tid in tests.keys()
                                if tests[tid].get('type') == 'auto-unittest'
                                and get_test_status(tid, 'auto-unittest', django_results,
                                                    selenium_results, accessibility_results)[0] == "✔Passed")  # CORRECTION: ajout d'indentation
            django_pct = (django_passed / django_total) * 100
            msg = f"   🐍 Django Unit Tests: {django_passed}/{django_total} ({django_pct:.1f}%)"
            print(msg)

        # Selenium
        selenium_total = stats['selenium_passed'] + stats['selenium_failed'] + stats['selenium_not_found']
        if selenium_total > 0:
            selenium_passed_pct = (stats['selenium_passed'] / selenium_total) * 100
            msg = f"   🌐 Selenium E2E: {stats['selenium_passed']}/{selenium_total} ({selenium_passed_pct:.1f}%)"
            print(msg)

        # ================ EXERCICE 18 : ACCESSIBILITÉ ================
        print("\n♿ ACCESSIBILITÉ (Exercice 18 - Pa11y)")

        accessibility_total = stats['accessibility_passed'] + stats['accessibility_failed'] + stats['accessibility_not_found']

        if accessibility_total > 0:
            if stats['accessibility_passed'] + stats['accessibility_failed'] > 0:
                avg_score = stats['accessibility_score'] / (stats['accessibility_passed'] + stats['accessibility_failed'])
            else:
                avg_score = 0

            accessibility_passed_pct = (stats['accessibility_passed'] / accessibility_total) * 100

            print(f"   Pages testées: {stats['accessibility_tests_executed']}")
            print(f"   Tests définis: {accessibility_total}")
            msg = f"   ✅ Tests réussis: {stats['accessibility_passed']}/{accessibility_total} ({accessibility_passed_pct:.1f}%)"
            print(msg)
            print(f"   📊 Score moyen: {avg_score:.1f}%")

            # Évaluation de la conformité
            if avg_score >= 100:
                print("   🏆 Conformité WGAC 2.1 Niveau A: ✅ PARFAIT!")
            elif avg_score >= 95:
                print("   👍 Conformité WGAC 2.1 Niveau A: ✅ EXCELLENT")
            elif avg_score >= 90:
                print("   ⚠️  Conformité WGAC 2.1 Niveau A: BON")
            elif avg_score >= 80:
                print("   ⚠️  Conformité WGAC 2.1 Niveau A: MOYEN")
            else:
                print("   ❗ Conformité WGAC 2.1 Niveau A: INSUFFISANT")

            # Détails des tests exécutés
            print("\n   📋 DÉTAIL DES TESTS EXÉCUTÉS:")
            for test_id, result in accessibility_results.items():
                score = result.get('score', 0)
                errors = result.get('errors_count', 0)
                warnings = result.get('warnings_count', 0)
                status_icon = "✅" if result.get('status') == 'passed' else "❌"
                print(f"     {status_icon} {test_id}: {result.get('url')}")
                print(f"        Score: {score}% | Erreurs: {errors} | Warnings: {warnings}")

                # Afficher les premières erreurs si présentes
                if errors > 0 and 'errors' in result:
                    for error in result['errors'][:2]:  # Limiter à 2 erreurs
                        error_msg = error.get('message', 'Unknown error')
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
            count = sum(1 for t in tests.values() if t.get('type') == type_key)
            if count > 0:
                passed = 0
                for tid in tests.keys():
                    if tests[tid].get('type') == type_key:
                        status, _ = get_test_status(tid, type_key, django_results,
                                                    selenium_results, accessibility_results)  # CORRECTION: indentation
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

    accessibility_tests = [(tid, tinfo) for tid, tinfo in tests.items()
                           if tinfo.get('type') == 'auto-accessibility']  # CORRECTION: indentation

    if accessibility_tests:
        print(f"✅ TESTS D'ACCESSIBILITÉ DÉTECTÉS: {len(accessibility_tests)}")
        print("\nDétails des tests d'accessibilité dans test_list.yaml:")

        for test_id, test_info in accessibility_tests:
            desc = test_info.get('description', 'Pas de description')
            expected_url = test_info.get('url', 'URL non spécifiée')
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

                if errors > 0:
                    print("     ❌ Problèmes détectés:")
                    for error in result.get('errors', [])[:3]:
                        context = error.get('context', '')
                        selector = error.get('selector', '')
                        print(f"        - {context[:50]}... [selector: {selector}]")
            else:
                msg = "     ⚠️  NON EXÉCUTÉ: Aucun résultat Pa11y pour ce test"
                print(msg)
                msg = f"     Vérifiez que l'URL {expected_url} est accessible"
                print(msg)
    else:
        print("⚠️  Aucun test 'auto-accessibility' trouvé dans test_list.yaml")
        print("\n💡 POUR AJOUTER DES TESTS D'ACCESSIBILITÉ:")
        print("1. Ajoutez dans test_list.yaml:")
        print("   TCXXX:")
        print("     type: auto-accessibility")
        print("     description: \"Test d'accessibilité de la page X\"")
        print("     url: \"http://127.0.0.1:8000/\"")
        print("\n2. Pa11y sera automatiquement exécuté pour ces tests")

    return stats


if __name__ == '__main__':
    main()
