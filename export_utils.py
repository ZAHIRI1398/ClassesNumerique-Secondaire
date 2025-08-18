import pandas as pd
from flask import send_file
import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
import tempfile

def generate_class_excel(class_data):
    """Génère un fichier Excel avec les statistiques de la classe"""
    # Créer un DataFrame pour les données des élèves
    student_data = []
    for student in class_data['students']:
        student_data.append({
            'Nom': student['student'].name or student['student'].username,
            'Exercices complétés': student['completed_exercises'],
            'Total exercices': student['total_exercises'],
            'Score moyen (%)': f"{student['average_score']:.1f}" if student['average_score'] is not None else "N/A",
            'Progression (%)': f"{(student['completed_exercises'] / student['total_exercises'] * 100):.1f}" if student['total_exercises'] > 0 else "0.0"
        })
    
    df = pd.DataFrame(student_data)
    
    # Créer un buffer pour stocker le fichier Excel
    output = io.BytesIO()
    
    # Créer un writer Excel
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Écrire les données dans une feuille
        df.to_excel(writer, sheet_name=f"Classe {class_data['class'].name}", index=False)
        
        # Récupérer la feuille de calcul
        worksheet = writer.sheets[f"Classe {class_data['class'].name}"]
        
        # Ajuster la largeur des colonnes
        for i, col in enumerate(df.columns):
            column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, column_width)
        
        # Ajouter un en-tête avec des informations générales
        worksheet.write(0, 6, "Informations générales")
        worksheet.write(1, 6, f"Nombre d'élèves: {len(class_data['students'])}")
        worksheet.write(2, 6, f"Total exercices: {class_data['total_exercises']}")
    
    # Réinitialiser le pointeur du buffer
    output.seek(0)
    
    return output

def generate_class_pdf(class_data):
    """Génère un fichier PDF avec les statistiques de la classe"""
    # Créer un buffer pour stocker le PDF
    buffer = io.BytesIO()
    
    # Créer le document PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Titre
    elements.append(Paragraph(f"Statistiques de la classe: {class_data['class'].name}", title_style))
    elements.append(Spacer(1, 12))
    
    # Informations générales
    elements.append(Paragraph("Informations générales", subtitle_style))
    elements.append(Spacer(1, 6))
    info_data = [
        ["Nombre d'élèves", str(len(class_data['students']))],
        ["Total exercices", str(class_data['total_exercises'])]
    ]
    info_table = Table(info_data, colWidths=[200, 100])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 12))
    
    # Tableau des élèves
    elements.append(Paragraph("Résultats par élève", subtitle_style))
    elements.append(Spacer(1, 6))
    
    # En-tête du tableau
    student_data = [["Élève", "Exercices complétés", "Score moyen (%)", "Progression (%)"]]
    
    # Données des élèves
    for student in class_data['students']:
        name = student['student'].name or student['student'].username
        completed = f"{student['completed_exercises']} / {student['total_exercises']}"
        avg_score = f"{student['average_score']:.1f}" if student['average_score'] is not None else "N/A"
        progress = f"{(student['completed_exercises'] / student['total_exercises'] * 100):.1f}" if student['total_exercises'] > 0 else "0.0"
        
        student_data.append([name, completed, avg_score, progress])
    
    # Créer le tableau
    student_table = Table(student_data, colWidths=[150, 100, 100, 100])
    student_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.white])
    ]))
    elements.append(student_table)
    
    # Construire le PDF
    doc.build(elements)
    
    # Réinitialiser le pointeur du buffer
    buffer.seek(0)
    
    return buffer
