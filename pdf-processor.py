import pytesseract
import pdf2image
import re
import sqlite3
import json
from datetime import datetime
import cv2
import numpy as np

class PDFTextExtractor:
    def __init__(self, db_path="extracted_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialise la base de données SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS extracted_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                prenom TEXT,
                date_naissance TEXT,
                numero_id TEXT,
                sexe TEXT,
                nationalite TEXT,
                adresse TEXT,
                date_extraction TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fichier_source TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def preprocess_image(self, image):
        """Prétraitement de l'image pour améliorer l'OCR"""
        # Conversion en niveaux de gris
        gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
        
        # Amélioration du contraste
        enhanced = cv2.equalizeHist(gray)
        
        # Débruitage
        denoised = cv2.fastNlMeansDenoising(enhanced)
        
        return denoised
    
    def extract_text_from_pdf(self, pdf_path):
        """Extrait le texte d'un PDF en utilisant OCR"""
        try:
            # Convertir PDF en images
            pages = pdf2image.convert_from_path(pdf_path, dpi=300)
            
            full_text = ""
            for page in pages:
                # Prétraitement de l'image
                processed_image = self.preprocess_image(page)
                
                # OCR avec Tesseract
                text = pytesseract.image_to_string(
                    processed_image, 
                    lang='fra+eng',
                    config='--psm 6'
                )
                full_text += text + "\n"
            
            return full_text
        
        except Exception as e:
            print(f"Erreur lors de l'extraction: {e}")
            return ""
    
    def analyze_id_card_advanced(self, text):
        """Analyse avancée pour extraire les informations de carte d'identité"""
        data = {
            'nom': '',
            'prenom': '',
            'date_naissance': '',
            'numero_id': '',
            'sexe': '',
            'nationalite': '',
            'adresse': ''
        }
        
        # Patterns plus sophistiqués
        patterns = {
            'nom': [
                r'(?:NOM|SURNAME|FAMILY\s+NAME)[\s:]+([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+)',
                r'APELLIDOS[\s:]+([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+)'
            ],
            'prenom': [
                r'(?:PRÉNOM|PRENOM|GIVEN\s+NAME|FIRST\s+NAME)[\s:]+([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+)',
                r'NOMBRE[\s:]+([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+)'
            ],
            'date_naissance': [
                r'(?:NÉ\s+LE|NE\s+LE|BORN|DATE\s+DE\s+NAISSANCE|FECHA\s+DE\s+NACIMIENTO)[\s:]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})',
                r'(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})'
            ],
            'numero_id': [
                r'(?:N°|NO|NUMBER|NUMÉRO|NUMERO)[\s:]*([A-Z0-9]+)',
                r'([A-Z]{2}\d{6,})'
            ],
            'sexe': [
                r'(?:SEXE|SEX|GENDER)[\s:]+(M|F|MASCULIN|FÉMININ|MALE|FEMALE)',
                r'\b(M|F)\b'
            ],
            'nationalite': [
                r'(?:NATIONALITÉ|NATIONALITY|NACIONALIDAD)[\s:]+([A-ZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞ\s]+)'
            ]
        }
        
        # Extraire les informations
        for field, pattern_list in patterns.items():
            for pattern in pattern_list:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match and not data[field]:
                    data[field] = match.group(1).strip()
                    break
        
        # Nettoyage des données
        self.clean_extracted_data(data)
        
        return data
    
    def clean_extracted_data(self, data):
        """Nettoie et valide les données extraites"""
        # Nettoyage du nom et prénom
        for field in ['nom', 'prenom']:
            if data[field]:
                data[field] = re.sub(r'[^A-Za-zÀ-ÿ\s\-]', '', data[field]).strip()
                data[field] = ' '.join(data[field].split())
        
        # Validation de la date
        if data['date_naissance']:
            # Normaliser le format de date
            date_match = re.search(r'(\d{1,2})[\/\-\.](\d{1,2})[\/\-\.](\d{4})', data['date_naissance'])
            if date_match:
                day, month, year = date_match.groups()
                data['date_naissance'] = f"{day.zfill(2)}/{month.zfill(2)}/{year}"
        
        # Nettoyage du numéro d'ID
        if data['numero_id']:
            data['numero_id'] = re.sub(r'[^A-Z0-9]', '', data['numero_id'].upper())
    
    def save_to_database(self, data, source_file):
        """Sauvegarde les données dans la base de données"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO extracted_data 
            (nom, prenom, date_naissance, numero_id, sexe, nationalite, adresse, fichier_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['nom'], data['prenom'], data['date_naissance'],
            data['numero_id'], data['sexe'], data['nationalite'],
            data['adresse'], source_file
        ))
        
        conn.commit()
        conn.close()
    
    def process_pdf_file(self, pdf_path):
        """Traite un fichier PDF complet"""
        print(f"Traitement du fichier: {pdf_path}")
        
        # Extraction du texte
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text.strip():
            print("Aucun texte extrait du PDF")
            return None
        
        # Analyse des données
        extracted_data = self.analyze_id_card_advanced(text)
        
        # Sauvegarde en base
        self.save_to_database(extracted_data, pdf_path)
        
        print("Données extraites et sauvegardées avec succès!")
        return extracted_data

# Exemple d'utilisation
if __name__ == "__main__":
    extractor = PDFTextExtractor()
    
    # Traiter un fichier PDF
    pdf_file = "carte_identite.pdf"
    result = extractor.process_pdf_file(pdf_file)
    
    if result:
        print("Données extraites:")
        for key, value in result.items():
            print(f"{key}: {value}")
