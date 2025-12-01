#!/usr/bin/env python3
"""
Script de rapport de tests - Exercice 11
Modifié pour prendre en compte les tests "auto-selenium"
et lire result_test_selenium.json
"""

import yaml
import json


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
    """EXERCICE 11: Charge les résultats des tests Selenium depuis JSON."""
    try:
        with open('result_test_selenium.json', 'r') as f:
            data = json.load(f)
            # IMPORTANT: Retourne seulement la section "tests"
            tests = data.get('tests', {})
            count = len(tests)

            if 'summary' in data:
                passed = data['summary'].get('passed', 0)
                failed = data['summary'].get('failed', 0)
                msg = f"✅ Fichier result_test_selenium.json chargé ({count} tests, {passed}✅ {failed}❌)"  # noqa: E501
                print(msg)
            else:
                msg = f"✅ Fichier result_test_selenium.json chargé ({count} tests Selenium)"  # noqa: E501
                print(msg)

            return tests
    except FileNotFoundError:
        msg = "⚠️  result_test_selenium.json non trouvé (tests Selenium non disponibles)"  # noqa: E501
        print(msg)
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur JSON dans result_test_selenium.json: {e}")
        return {}


def get_test_status(test_id, test_type, django_results, selenium_results):
    """EXERCICE 11: Détermine le statut d'un test, y compris auto-selenium."""
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
        # EXERCICE 11: Vérification spécifique dans les résultats Selenium
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

    return "💬Type inconnu", "❓"


def main():
    """Génère le rapport de tests avec support Selenium."""

    print("📊 Génération du rapport de tests...")
    print("Lecture des tests auto via result_test_auto.json…")
    print("Lecture des tests Selenium via result_test_selenium.json…")
    print()

    tests = load_test_list()
    django_results = load_django_results()
    selenium_results = load_selenium_results()  # EXERCICE 11

    print("OK")
    print()

    # Initialise les compteurs
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'not_found': 0,
        'manual': 0,
        'selenium_passed': 0,   # EXERCICE 11: stats Selenium
        'selenium_failed': 0,   # EXERCICE 11: stats Selenium
        'selenium_not_found': 0  # EXERCICE 11: stats Selenium
    }

    # ================ EXERCICE 5 : RAPPORT VISUEL ================
    print("=" * 60)
    print("RAPPORT DES TESTS (avec Selenium)")
    print("=" * 60)

    # Affiche chaque test
    for test_id in sorted(tests.keys()):
        stats['total'] += 1
        test_info = tests[test_id]
        test_type = test_info.get('type', 'unknown')

        # EXERCICE 11: Utilisation de la fonction améliorée
        status, icon = get_test_status(test_id, test_type, django_results, selenium_results)  # noqa: E501

        # Mettre à jour les statistiques générales
        if status == "✔Passed":
            stats['passed'] += 1
            if test_type == 'auto-selenium':  # EXERCICE 11
                stats['selenium_passed'] += 1
        elif status == "✘Failed":
            stats['failed'] += 1
            if test_type == 'auto-selenium':  # EXERCICE 11
                stats['selenium_failed'] += 1
        elif status == "💬Not found":
            stats['not_found'] += 1
            if test_type == 'auto-selenium':  # EXERCICE 11
                stats['selenium_not_found'] += 1
        elif status == "💬Manual test needed":
            stats['manual'] += 1

        # Afficher la ligne du test
        print(f"{icon} {test_id:6} | {test_type:15} | {status:20}")

    print("=" * 60)

    # ================ EXERCICE 6 : STATISTIQUES ================
    print()
    print("📈 STATISTIQUES")
    print("-" * 40)

    if stats['total'] > 0:
        # Calcule les pourcentages
        passed_pct = (stats['passed'] / stats['total']) * 100
        failed_pct = (stats['failed'] / stats['total']) * 100
        not_found_pct = (stats['not_found'] / stats['total']) * 100
        manual_pct = (stats['manual'] / stats['total']) * 100

        print(f"Number of tests: {stats['total']}")
        print(f"✔Passed tests: {stats['passed']} ({passed_pct:.1f}%)")
        print(f"✘Failed tests: {stats['failed']} ({failed_pct:.1f}%)")
        print(f"💬Not found tests: {stats['not_found']} ({not_found_pct:.1f}%)")
        print(f"👥Test to pass manually: {stats['manual']} ({manual_pct:.1f}%)")
        print()
        total_ok = stats['passed'] + stats['manual']
        total_ok_pct = passed_pct + manual_pct
        print(f"✔Passed + 👥Manual: {total_ok} ({total_ok_pct:.1f}%)")

        # ================ EXERCICE 11 : STATS SPÉCIFIQUES SELENIUM ================
        print()
        print("🔧 STATISTIQUES SELENIUM (Exercice 11)")
        print("-" * 40)

        selenium_total = (stats['selenium_passed'] + stats['selenium_failed'] + stats['selenium_not_found'])  # noqa: E501
        if selenium_total > 0:
            selenium_passed_pct = (stats['selenium_passed'] / selenium_total) * 100  # noqa: E501
            selenium_failed_pct = (stats['selenium_failed'] / selenium_total) * 100  # noqa: E501
            selenium_not_found_pct = (stats['selenium_not_found'] / selenium_total) * 100  # noqa: E501

            print(f"Tests Selenium exécutés: {selenium_total}")
            msg1 = f"  ✅ Selenium passés: {stats['selenium_passed']} ({selenium_passed_pct:.1f}%)"  # noqa: E501
            print(msg1)
            msg2 = f"  ❌ Selenium échoués: {stats['selenium_failed']} ({selenium_failed_pct:.1f}%)"  # noqa: E501
            print(msg2)
            msg3 = f"  ❓ Selenium non trouvés: {stats['selenium_not_found']} ({selenium_not_found_pct:.1f}%)"  # noqa: E501
            print(msg3)
        else:
            print("Aucun test Selenium trouvé dans le cahier")

        # ================ EXERCICE 11 : RÉCAPITULATIF ================
        print()
        print("📋 RÉCAPITULATIF PAR TYPE")
        print("-" * 40)

        # Compter par type
        type_counts = {'auto-unittest': 0, 'auto-selenium': 0, 'manuel': 0}
        type_passed = {'auto-unittest': 0, 'auto-selenium': 0, 'manuel': 0}

        for test_id, test_info in tests.items():
            test_type = test_info.get('type', 'unknown')
            if test_type in type_counts:
                type_counts[test_type] += 1

                # Vérifier si le test a réussi
                status, _ = get_test_status(test_id, test_type, django_results, selenium_results)  # noqa: E501
                if status == "✔Passed":
                    type_passed[test_type] += 1

        for test_type in ['auto-unittest', 'auto-selenium', 'manuel']:
            count = type_counts[test_type]
            if count > 0:
                passed = type_passed[test_type]
                pct = (passed / count) * 100 if count > 0 else 0
                type_name = {
                    'auto-unittest': 'Tests Django',
                    'auto-selenium': 'Tests Selenium',
                    'manuel': 'Tests manuels'
                }[test_type]
                print(f"{type_name:20} : {passed}/{count} réussis ({pct:.1f}%)")

    else:
        print("❌ Aucun test trouvé!")

    # ================ EXERCICE 11 : VÉRIFICATION ================
    print()
    print("=" * 60)
    print("VÉRIFICATION EXERCICE 11")
    print("=" * 60)

    # Vérifier qu'on a bien des tests auto-selenium
    selenium_tests = [t for t in tests.items() if t[1].get('type') == 'auto-selenium']  # noqa: E501

    if selenium_tests:
        msg = f"✅ {len(selenium_tests)} test(s) 'auto-selenium' détecté(s) dans test_list.yaml:"  # noqa: E501
        print(msg)
        for test_id, test_info in selenium_tests:
            desc = test_info.get('description', 'Pas de description')
            print(f"   - {test_id}: {desc}")

        # Vérifier les résultats correspondants
        print("\n🔍 Résultats Selenium correspondants:")
        for test_id, _ in selenium_tests:
            if test_id in selenium_results:
                result = selenium_results[test_id]
                status = result.get('status', 'inconnu')
                message = result.get('message', 'Pas de message')
                print(f"   - {test_id}: {status} - {message[:50]}...")
            else:
                msg = f"   - {test_id}: ❌ Aucun résultat dans result_test_selenium.json"  # noqa: E501
                print(msg)
    else:
        print("⚠️  Aucun test 'auto-selenium' trouvé dans test_list.yaml")
        msg = "   Assurez-vous d'avoir ajouté des tests avec type: 'auto-selenium'"
        print(msg)

    return stats


if __name__ == '__main__':
    main()
