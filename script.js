let extractedDatabase = [];

// Configuration PDF.js
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.worker.min.js';

async function processPDF() {
    const fileInput = document.getElementById('pdfFile');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Veuillez sélectionner un fichier PDF');
        return;
    }
    
    try {
        const arrayBuffer = await file.arrayBuffer();
        const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
        
        let fullText = '';
        
        // Extraire le texte de chaque page
        for (let i = 1; i <= pdf.numPages; i++) {
            const page = await pdf.getPage(i);
            const textContent = await page.getTextContent();
            const pageText = textContent.items.map(item => item.str).join(' ');
            fullText += pageText + '\n';
        }
        
        // Analyser le texte pour détecter les informations de carte d'identité
        const extractedInfo = analyzeIDCard(fullText);
        displayExtractedData(extractedInfo);
        
    } catch (error) {
        console.error('Erreur lors du traitement du PDF:', error);
        alert('Erreur lors du traitement du fichier PDF');
    }
}

function analyzeIDCard(text) {
    const idCardInfo = {
        nom: '',
        prenom: '',
        dateNaissance: '',
        numeroID: '',
        adresse: '',
        sexe: '',
        nationalite: ''
    };
    
    // Expressions régulières pour extraire les informations
    const patterns = {
        nom: /(?:NOM|SURNAME|FAMILY NAME)[:\s]+([A-Z\s]+)/i,
        prenom: /(?:PRÉNOM|PRENOM|GIVEN NAME|FIRST NAME)[:\s]+([A-Z\s]+)/i,
        dateNaissance: /(?:NÉ|NE|BORN|DATE DE NAISSANCE)[:\s]+(\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{4})/i,
        numeroID: /(?:N°|NO|NUMBER|NUMÉRO)[:\s]*([A-Z0-9]+)/i,
        sexe: /(?:SEXE|SEX|GENDER)[:\s]+(M|F|MASCULIN|FÉMININ|MALE|FEMALE)/i,
        nationalite: /(?:NATIONALITÉ|NATIONALITY)[:\s]+([A-Z\s]+)/i
    };
    
    // Extraire les informations en utilisant les patterns
    for (const [key, pattern] of Object.entries(patterns)) {
        const match = text.match(pattern);
        if (match) {
            idCardInfo[key] = match[1].trim();
        }
    }
    
    // Nettoyage et formatage des données
    idCardInfo.nom = idCardInfo.nom.replace(/[^A-Za-z\s]/g, '').trim();
    idCardInfo.prenom = idCardInfo.prenom.replace(/[^A-Za-z\s]/g, '').trim();
    
    return idCardInfo;
}

function displayExtractedData(data) {
    const resultsDiv = document.getElementById('extractedData');
    const exportBtn = document.getElementById('exportBtn');
    
    resultsDiv.innerHTML = `
        <div class="extracted-info">
            <h4>Informations extraites:</h4>
            <p><strong>Nom:</strong> ${data.nom || 'Non détecté'}</p>
            <p><strong>Prénom:</strong> ${data.prenom || 'Non détecté'}</p>
            <p><strong>Date de naissance:</strong> ${data.dateNaissance || 'Non détecté'}</p>
            <p><strong>Numéro ID:</strong> ${data.numeroID || 'Non détecté'}</p>
            <p><strong>Sexe:</strong> ${data.sexe || 'Non détecté'}</p>
            <p><strong>Nationalité:</strong> ${data.nationalite || 'Non détecté'}</p>
        </div>
    `;
    
    // Stocker les données pour l'export
    window.currentExtractedData = data;
    exportBtn.style.display = 'block';
}

function exportToDatabase() {
    const data = window.currentExtractedData;
    if (!data) return;
    
    // Ajouter timestamp
    data.dateExtraction = new Date().toLocaleString();
    
    // Ajouter à la base de données locale
    extractedDatabase.push(data);
    
    // Mettre à jour l'affichage de la table
    updateDataTable();
    
    alert('Données ajoutées à la base de données!');
}

function updateDataTable() {
    const tableBody = document.getElementById('tableBody');
    tableBody.innerHTML = '';
    
    extractedDatabase.forEach((entry, index) => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${entry.nom}</td>
            <td>${entry.prenom}</td>
            <td>${entry.dateNaissance}</td>
            <td>${entry.numeroID}</td>
            <td>${entry.dateExtraction}</td>
        `;
    });
}

function exportToCSV() {
    if (extractedDatabase.length === 0) {
        alert('Aucune donnée à exporter');
        return;
    }
    
    const headers = ['Nom', 'Prénom', 'Date de naissance', 'Numéro ID', 'Sexe', 'Nationalité', 'Date d\'extraction'];
    const csvContent = [
        headers.join(','),
        ...extractedDatabase.map(entry => [
            entry.nom,
            entry.prenom,
            entry.dateNaissance,
            entry.numeroID,
            entry.sexe,
            entry.nationalite,
            entry.dateExtraction
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'extracted_data.csv';
    a.click();
    window.URL.revokeObjectURL(url);
}

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    console.log('PDF AI Extractor initialized');
});
