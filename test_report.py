#!/usr/bin/env python3
"""
Script de rapport de tests - Exercice 5 & 6
Lecture de test_list.yaml et result_test_auto.json avec statistiques.
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


def load_test_results():
    """Charge les résultats des tests depuis JSON."""
    try:
        with open('result_test_auto.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  result_test_auto.json non trouvé")
        return {}
    except json.JSONDecodeError as e:
        print(f"⚠️  Erreur JSON: {e}")
        return {}


def main():
    """Génère le rapport de tests visuel avec statistiques."""

    print("Lecture des tests auto via result_test_auto.json…")
    print()
    print("OK")

    tests = load_test_list()
    results = load_test_results()

    # Initialise les compteurs
    stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'not_found': 0,
        'manual': 0
    }

    # Affiche chaque test et compte
    for test_id in sorted(tests.keys()):
        stats['total'] += 1
        test_info = tests[test_id]
        test_type = test_info.get('type', 'unknown')

        if test_type == 'manuel':
            stats['manual'] += 1
            print(f"{test_id} | manual | 💬Manual test needed")

        elif test_type == 'auto-unittest':
            result = results.get(test_id, {})
            status = result.get('status', 'not_found')

            if status == 'passed':
                stats['passed'] += 1
                print(f"{test_id} | auto | ✔Passed")
            elif status == 'failed':
                stats['failed'] += 1
                print(f"{test_id} | auto | ✘Failed")
            else:  # not_found, error, etc.
                stats['not_found'] += 1
                print(f"{test_id} | auto | 💬Not found")

    # ================ EXERCICE 6 : STATISTIQUES ================
    print()
    print("=" * 50)
    print("📊 RAPPORT DE TESTS")
    print("=" * 50)

    print(f"Number of tests: {stats['total']}")

    if stats['total'] > 0:
        # Calcule les pourcentages
        passed_pct = (stats['passed'] / stats['total']) * 100
        failed_pct = (stats['failed'] / stats['total']) * 100
        not_found_pct = (stats['not_found'] / stats['total']) * 100
        manual_pct = (stats['manual'] / stats['total']) * 100

        # Affiche les statistiques
        print(
            f"✔Passed tests: {stats['passed']} ({passed_pct:.1f}%)"
        )
        print(
            f"✘Failed tests: {stats['failed']} ({failed_pct:.1f}%)"
        )
        print(
            f"💬Not found tests: "
            f"{stats['not_found']} ({not_found_pct:.1f}%)"
        )
        print(
            f"👥Test to pass manually: "
            f"{stats['manual']} ({manual_pct:.1f}%)"
        )
        print()
        total_ok = stats['passed'] + stats['manual']
        total_ok_pct = passed_pct + manual_pct
        print(f"✔Passed + 👥Manual: {total_ok} ({total_ok_pct:.1f}%)")
    else:
        print("❌ Aucun test trouvé!")


if __name__ == '__main__':
    main()
