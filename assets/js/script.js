<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Abdellaoui Abdelilah - Portfolio</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header>
    <h1>Abdellaoui Abdelilah</h1>
    <nav>
      <a href="#about">About</a>
      <a href="#projects">Projects</a>
      <a href="#pdf-extractor">PDF AI Extractor</a>
      <a href="#contact">Contact</a>
    </nav>
  </header>

  <main>
    <section id="about">
      <h2>About Me</h2>
      <p>Développeur passionné par l'intelligence artificielle et l'automatisation. Spécialisé dans la création d'outils innovants pour l'extraction et le traitement de données.</p>
    </section>

    <section id="projects">
      <h2>Projects</h2>
      <ul class="project-list">
        <li class="project">
          <h3>PDF AI Text Extractor</h3>
          <p>Application IA pour extraire automatiquement du texte des PDF et cartes d'identité, avec création de base de données structurée.</p>
          <a href="#pdf-extractor" class="project-link">Utiliser l'outil</a>
        </li>
      </ul>
    </section>

    <section id="pdf-extractor">
      <h2>PDF AI Text Extractor</h2>
      <div class="extractor-container">
        <div class="upload-area">
          <h3>Télécharger un fichier PDF</h3>
          <input type="file" id="pdfFile" accept=".pdf" />
          <button onclick="processPDF()">Extraire le texte</button>
        </div>
        
        <div class="results-area">
          <h3>Résultats d'extraction</h3>
          <div id="extractedData" class="data-display"></div>
          <button onclick="exportToDatabase()" style="display:none;" id="exportBtn">Exporter vers base de données</button>
        </div>
        
        <div class="database-area">
          <h3>Base de données</h3>
          <table id="dataTable" class="data-table">
            <thead>
              <tr>
                <th>Nom</th>
                <th>Prénom</th>
                <th>Date de naissance</th>
                <th>Numéro ID</th>
                <th>Date d'extraction</th>
              </tr>
            </thead>
            <tbody id="tableBody">
            </tbody>
          </table>
          <button onclick="exportToCSV()">Exporter en CSV</button>
        </div>
      </div>
    </section>

    <section id="contact">
      <h2>Contact</h2>
      <p>Email: abdellaoui.abdelilah@example.com</p>
      <p>GitHub: github.com/abdou</p>
    </section>
  </main>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.11.338/pdf.min.js"></script>
  <script src="assets/js/script.js"></script>
</body>
</html>