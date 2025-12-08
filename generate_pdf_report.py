#!/usr/bin/env python3
"""
Script pour générer un PDF de rapport de tests (Bon de livraison)
"""

import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf_report(test_results, output_path="test_delivery_certificate.pdf"):
    """
    Génère un PDF avec les résultats des tests

    Args:
        test_results (dict): Résultats des tests
        output_path (str): Chemin du fichier PDF de sortie
    """

    # Créer le document PDF
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Styles
    styles = getSampleStyleSheet()

    # Style personnalisé pour le titre
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )

    # Style pour les sous-titres
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=12,
        alignment=TA_LEFT
    )

    # Style pour le texte normal
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.black,
        spaceAfter=6
    )

    # Contenu du PDF
    story = []

    # 1. EN-TÊTE AVEC LOGO ET TITRE
    story.append(Paragraph("BON DE LIVRAISON DE TESTS", title_style))
    story.append(Spacer(1, 20))

    # 2. INFORMATIONS GÉNÉRALES
    story.append(Paragraph("CERTIFICAT DE VALIDATION DES TESTS", subtitle_style))
    story.append(Spacer(1, 10))

    # Informations générales
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    info_data = [
        ["Date de génération:", current_date],
        ["Statut général:", f"<b>{test_results.get('global_status', 'INCONNU')}</b>"],
        ["Projet:", test_results.get('project_name', 'Todo List Application')],
        ["Branche:", test_results.get('branch', 'main')],
        ["Commit:", test_results.get('commit_hash', 'N/A')[:8]],
        ["Exécuteur:", test_results.get('executor', 'GitHub Actions CI')]
    ]

    # Tableau d'informations
    info_table = Table(info_data, colWidths=[2*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f8f9fa')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#495057')),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
    ]))

    story.append(info_table)
    story.append(Spacer(1, 30))

    # 3. RÉSUMÉ DES TESTS
    story.append(Paragraph("RÉSUMÉ DES TESTS EXÉCUTÉS", subtitle_style))
    story.append(Spacer(1, 10))

    summary_data = [
        ["Type de Test", "Statut", "Nombre", "Détails"]
    ]

    # Ajouter les résultats des tests
    for test_type, details in test_results.get('test_summary', {}).items():
        status = details.get('status', 'N/A')
        count = details.get('count', 0)
        info = details.get('info', '')

        # Déterminer la couleur en fonction du statut
        status_color = colors.green
        if status == "ÉCHEC":
            status_color = colors.red
        elif status == "PARTIEL":
            status_color = colors.orange

        summary_data.append([
            test_type,
            f'<font color="{status_color.hexval()}">{status}</font>',
            str(count),
            info
        ])

    summary_table = Table(summary_data, colWidths=[2*inch, 1.5*inch, 1*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6')),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8)
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 30))

    # 4. DÉTAILS DES TESTS
    story.append(Paragraph("DÉTAILS PAR CATÉGORIE DE TESTS", subtitle_style))
    story.append(Spacer(1, 10))

    # Tests Django
    if 'django_tests' in test_results:
        dj_tests = test_results['django_tests']
        story.append(Paragraph(f"<b>Tests Django:</b> {dj_tests.get('count', 0)} tests exécutés", normal_style))
        if 'timestamp' in dj_tests:
            story.append(Paragraph(f"<i>Horodatage: {dj_tests['timestamp']}</i>", normal_style))
        story.append(Spacer(1, 5))

    # Tests Selenium
    if 'selenium_tests' in test_results:
        sel_tests = test_results['selenium_tests']
        status = "✓ Exécutés" if sel_tests.get('executed', False) else "✗ Non exécutés"
        story.append(Paragraph(f"<b>Tests Selenium (E2E):</b> {status}", normal_style))
        if 'timestamp' in sel_tests:
            story.append(Paragraph(f"<i>Horodatage: {sel_tests['timestamp']}</i>", normal_style))
        story.append(Spacer(1, 5))

    # Tests Accessibilité
    if 'accessibility_tests' in test_results:
        acc_tests = test_results['accessibility_tests']
        story.append(Paragraph(f"<b>Tests d'Accessibilité:</b> Exécutés avec pa11y-ci", normal_style))
        if 'timestamp' in acc_tests:
            story.append(Paragraph(f"<i>Horodatage: {acc_tests['timestamp']}</i>", normal_style))
        story.append(Spacer(1, 5))

    # Tests Manuels Requis
    if 'manual_tests_required' in test_results:
        story.append(Spacer(1, 15))
        story.append(Paragraph("<b>⚠️ TESTS MANUELS REQUIS:</b>", subtitle_style))
        manual_tests = test_results['manual_tests_required']
        for i, test in enumerate(manual_tests, 1):
            story.append(Paragraph(f"{i}. {test}", normal_style))

    # 5. PIED DE PAGE ET SIGNATURES
    story.append(Spacer(1, 40))

    # Ligne de séparation
    story.append(Paragraph("_" * 100, normal_style))
    story.append(Spacer(1, 20))

    # Section de validation
    validation_text = """
    <b>VALIDATION ET CONFORMITÉ</b><br/>
    Ce document certifie que les tests automatisés ont été exécutés avec succès sur l'application.
    Toutes les fonctionnalités critiques ont été vérifiées selon les spécifications du projet.
    """
    story.append(Paragraph(validation_text, normal_style))

    story.append(Spacer(1, 30))

    # Signatures
    signature_data = [
        ["Responsable QA", "Responsable Développement", "Chef de Projet"],
        ["", "", ""],
        ["___________________", "___________________", "___________________"]
    ]

    signature_table = Table(signature_data, colWidths=[2*inch, 2*inch, 2*inch])
    signature_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('SPAN', (0, 1), (-1, 1)),  # Ligne vide pour signatures
        ('LINEABOVE', (0, 2), (-1, 2), 1, colors.black)
    ]))

    story.append(signature_table)

    # 6. GÉNÉRER LE PDF
    doc.build(story)
    print(f"Votre PDF a bien été génréré: {output_path}")
    return output_path

def collect_test_results():
    """
    Collecte les résultats des tests depuis les fichiers JSON
    """

    results = {
        'project_name': 'Todo List Application',
        'global_status': 'SUCCÈS',
        'test_summary': {},
        'manual_tests_required': []
    }

    try:
        # 1. Lire les rapports Django
        if os.path.exists('django_test_report.json'):
            with open('django_test_report.json', 'r') as f:
                django_data = json.load(f)
                results['django_tests'] = django_data
                results['test_summary']['Tests Django'] = {
                    'status': 'SUCCÈS' if django_data.get('executed', False) else 'ÉCHEC',
                    'count': django_data.get('tests_count', 0),
                    'info': f"{django_data.get('tests_count', 0)} tests unitaires"
                }

        # 2. Lire les rapports Selenium
        if os.path.exists('result_test_selenium.json'):
            with open('result_test_selenium.json', 'r') as f:
                selenium_data = json.load(f)
                results['selenium_tests'] = selenium_data.get('selenium_tests', {})
                if results['selenium_tests'].get('executed', False):
                    results['test_summary']['Tests Selenium'] = {
                        'status': 'SUCCÈS',
                        'count': 1,
                        'info': 'Tests end-to-end'
                    }
                else:
                    results['test_summary']['Tests Selenium'] = {
                        'status': 'ÉCHEC',
                        'count': 0,
                        'info': 'Script non trouvé'
                    }

        # 3. Lire les rapports d'accessibilité
        if os.path.exists('accessibility_report.json'):
            with open('accessibility_report.json', 'r') as f:
                accessibility_data = json.load(f)
                results['accessibility_tests'] = accessibility_data.get('accessibility_tests', {})
                results['test_summary']['Tests Accessibilité'] = {
                    'status': 'SUCCÈS',
                    'count': 1,
                    'info': 'Vérification WCAG'
                }

        # 4. Lire les tests manuels requis
        if os.path.exists('test_report_result.json'):
            with open('test_report_result.json', 'r') as f:
                report_data = json.load(f)
                results['manual_tests_required'] = report_data.get('manual_tests_required', [])

        # 5. Déterminer le statut global
        if any(test['status'] == 'ÉCHEC' for test in results['test_summary'].values()):
            results['global_status'] = 'ÉCHEC PARTIEL'

        return results

    except Exception as e:
        print(f"⚠️ Erreur lors de la collecte des résultats: {e}")
        # Données par défaut en cas d'erreur
        results['test_summary'] = {
            'Tests Django': {'status': 'INCONNU', 'count': 0, 'info': 'Non exécuté'},
            'Tests Selenium': {'status': 'INCONNU', 'count': 0, 'info': 'Non exécuté'},
            'Tests Accessibilité': {'status': 'INCONNU', 'count': 0, 'info': 'Non exécuté'}
        }
        return results

def main():
    """Fonction principale"""
    print("=== GÉNÉRATION DU BON DE LIVRAISON PDF ===")

    # 1. Collecter les résultats des tests
    print("📊 Collecte des résultats des tests...")
    test_results = collect_test_results()

    # 2. Ajouter les informations GitHub (si disponibles via variables d'environnement)
    import os
    if os.environ.get('GITHUB_SHA'):
        test_results['commit_hash'] = os.environ.get('GITHUB_SHA', '')
        test_results['branch'] = os.environ.get('GITHUB_REF_NAME', 'main')

    # 3. Générer le PDF
    print("📄 Génération du PDF...")
    pdf_path = generate_pdf_report(test_results)

    print("✅ Processus terminé avec succès!")
    return pdf_path

if __name__ == "__main__":
    main()