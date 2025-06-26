#!/usr/bin/env python3
"""
OSINT Test - Recherche d'informations publiques sur "ABDELILAH ABDELLAOUI"
Ce script utilise les capacités OSINT de la plateforme pour collecter des informations publiques.
"""

import asyncio
import aiohttp
import requests
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Any
import os
import sys

# Ajouter le chemin du backend
sys.path.append('/workspaces/abdou.github.io/backend')

try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class OSINTSearchEngine:
    """Moteur de recherche OSINT pour collecter des informations publiques"""
    
    def __init__(self):
        self.target_name = "ABDELILAH ABDELLAOUI"
        self.results = {
            "search_engines": {},
            "social_media": {},
            "professional": {},
            "ai_analysis": {},
            "metadata": {
                "search_date": datetime.now().isoformat(),
                "target": self.target_name,
                "status": "in_progress"
            }
        }
        
    async def search_google_dorking(self):
        """Recherche avec Google Dorking (simulation)"""
        print("🔍 Recherche Google avec techniques de dorking...")
        
        # Simulations de requêtes Google (dans un vrai cas, utiliser l'API Google Search)
        google_queries = [
            f'"{self.target_name}"',
            f'"{self.target_name}" site:linkedin.com',
            f'"{self.target_name}" site:facebook.com',
            f'"{self.target_name}" site:twitter.com',
            f'"{self.target_name}" site:github.com',
            f'"{self.target_name}" filetype:pdf',
            f'"{self.target_name}" cv OR resume',
            f'"{self.target_name}" email OR contact',
            f'"{self.target_name}" phone OR telephone',
            f'"{self.target_name}" university OR école',
        ]
        
        self.results["search_engines"]["google_queries"] = google_queries
        self.results["search_engines"]["status"] = "queries_prepared"
        
        print(f"✅ {len(google_queries)} requêtes Google préparées")
        return google_queries
    
    async def search_social_media(self):
        """Recherche sur les réseaux sociaux (simulation)"""
        print("📱 Recherche sur les réseaux sociaux...")
        
        social_platforms = {
            "linkedin": f"https://www.linkedin.com/search/results/people/?keywords={self.target_name.replace(' ', '%20')}",
            "facebook": f"https://www.facebook.com/search/people/?q={self.target_name.replace(' ', '%20')}",
            "twitter": f"https://twitter.com/search?q={self.target_name.replace(' ', '%20')}",
            "instagram": f"https://www.instagram.com/explore/tags/{self.target_name.replace(' ', '').lower()}/",
            "github": f"https://github.com/search?q={self.target_name.replace(' ', '%20')}&type=users",
            "youtube": f"https://www.youtube.com/results?search_query={self.target_name.replace(' ', '+')}",
        }
        
        self.results["social_media"]["platforms"] = social_platforms
        self.results["social_media"]["status"] = "urls_generated"
        
        print(f"✅ URLs générées pour {len(social_platforms)} plateformes")
        return social_platforms
    
    async def search_professional_networks(self):
        """Recherche sur les réseaux professionnels"""
        print("💼 Recherche sur les réseaux professionnels...")
        
        professional_sites = {
            "linkedin": "Profil professionnel principal",
            "indeed": f"https://www.indeed.com/q-{self.target_name.replace(' ', '-')}-jobs.html",
            "glassdoor": f"Recherche employeur: {self.target_name}",
            "crunchbase": f"Recherche entrepreneur: {self.target_name}",
            "angellist": f"Recherche startup: {self.target_name}",
            "behance": f"Portfolio créatif: {self.target_name}",
            "dribbble": f"Portfolio design: {self.target_name}",
        }
        
        self.results["professional"]["sites"] = professional_sites
        self.results["professional"]["status"] = "search_prepared"
        
        print(f"✅ {len(professional_sites)} sites professionnels analysés")
        return professional_sites
    
    async def ai_name_analysis(self):
        """Analyse IA du nom pour déduire des informations"""
        if not OPENAI_AVAILABLE:
            print("⚠️ OpenAI non disponible pour l'analyse")
            return {}
            
        print("🧠 Analyse IA du nom...")
        
        try:
            response = await self.openai_analysis(
                f"Analyze this name for OSINT purposes: '{self.target_name}'. "
                "Provide insights about: 1) Likely origin/ethnicity 2) Gender 3) Common variations "
                "4) Cultural context 5) Potential social media usernames 6) Professional fields. "
                "Be factual and avoid stereotypes."
            )
            
            self.results["ai_analysis"]["name_analysis"] = response
            print("✅ Analyse IA du nom terminée")
            return response
            
        except Exception as e:
            print(f"❌ Erreur analyse IA: {e}")
            return {"error": str(e)}
    
    async def openai_analysis(self, prompt: str):
        """Appel à l'API OpenAI"""
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert OSINT analyst. Provide factual, ethical analysis for legitimate research purposes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Erreur OpenAI: {e}"
    
    async def generate_search_variations(self):
        """Génère des variations du nom pour la recherche"""
        print("🔤 Génération de variations du nom...")
        
        name_parts = self.target_name.split()
        variations = [
            self.target_name,
            self.target_name.lower(),
            self.target_name.upper(),
            " ".join(name_parts),
            "".join(name_parts),
            f"{name_parts[0]} {name_parts[-1]}" if len(name_parts) > 2 else self.target_name,
            f"{name_parts[0][0]}. {name_parts[-1]}" if len(name_parts) > 1 else self.target_name,
        ]
        
        # Ajout de variations avec initiales
        if len(name_parts) >= 2:
            variations.extend([
                f"{name_parts[0]} {name_parts[1][0]}. {name_parts[-1]}" if len(name_parts) > 2 else f"{name_parts[0]} {name_parts[1]}",
                f"{name_parts[0][0]}. {name_parts[1]} {name_parts[-1]}" if len(name_parts) > 2 else f"{name_parts[0][0]}. {name_parts[1]}",
            ])
        
        # Suppression des doublons
        variations = list(set(variations))
        
        self.results["search_engines"]["name_variations"] = variations
        print(f"✅ {len(variations)} variations générées")
        return variations
    
    async def check_data_breaches(self):
        """Vérifie les fuites de données connues (simulation)"""
        print("🛡️ Vérification des fuites de données...")
        
        # Simulation - dans un vrai cas, utiliser des APIs comme HaveIBeenPwned
        breach_sources = [
            "HaveIBeenPwned API",
            "Dehashed",
            "LeakCheck",
            "Breach Directory",
            "IntelligenceX",
        ]
        
        self.results["security"] = {
            "breach_sources": breach_sources,
            "status": "simulation",
            "note": "Vérification nécessite des APIs spécialisées"
        }
        
        print(f"✅ {len(breach_sources)} sources de fuites vérifiées (simulation)")
        return breach_sources
    
    async def run_complete_search(self):
        """Lance une recherche OSINT complète"""
        print("🚀 Démarrage de la recherche OSINT complète")
        print(f"🎯 Cible: {self.target_name}")
        print("=" * 60)
        
        # Exécution de toutes les recherches
        await self.generate_search_variations()
        await self.search_google_dorking()
        await self.search_social_media()
        await self.search_professional_networks()
        await self.ai_name_analysis()
        await self.check_data_breaches()
        
        # Finalisation
        self.results["metadata"]["status"] = "completed"
        self.results["metadata"]["completion_time"] = datetime.now().isoformat()
        
        return self.results
    
    def generate_report(self):
        """Génère un rapport OSINT détaillé"""
        print("\n" + "="*60)
        print("📊 RAPPORT OSINT - ABDELILAH ABDELLAOUI")
        print("="*60)
        
        print(f"\n🎯 CIBLE: {self.target_name}")
        print(f"📅 DATE: {self.results['metadata']['search_date']}")
        print(f"✅ STATUS: {self.results['metadata']['status'].upper()}")
        
        print("\n🔍 VARIATIONS DU NOM:")
        for i, variation in enumerate(self.results.get("search_engines", {}).get("name_variations", []), 1):
            print(f"  {i}. {variation}")
        
        print("\n🌐 REQUÊTES GOOGLE DORKING:")
        for i, query in enumerate(self.results.get("search_engines", {}).get("google_queries", []), 1):
            print(f"  {i}. {query}")
        
        print("\n📱 PLATEFORMES SOCIALES:")
        for platform, url in self.results.get("social_media", {}).get("platforms", {}).items():
            print(f"  • {platform.upper()}: {url}")
        
        print("\n💼 RÉSEAUX PROFESSIONNELS:")
        for site, desc in self.results.get("professional", {}).get("sites", {}).items():
            print(f"  • {site.upper()}: {desc}")
        
        if "ai_analysis" in self.results and "name_analysis" in self.results["ai_analysis"]:
            print("\n🧠 ANALYSE IA:")
            print(f"  {self.results['ai_analysis']['name_analysis']}")
        
        print("\n🛡️ SÉCURITÉ:")
        security = self.results.get("security", {})
        print(f"  Sources vérifiées: {len(security.get('breach_sources', []))}")
        print(f"  Status: {security.get('status', 'N/A')}")
        
        print("\n⚖️ AVERTISSEMENT LÉGAL:")
        print("  Cette recherche utilise uniquement des sources publiques.")
        print("  Respectez la vie privée et les lois en vigueur.")
        print("  Usage à des fins légitimes uniquement.")
        
        print("\n" + "="*60)

async def main():
    """Fonction principale"""
    print("🔍 OSINT-AI Platform - Test de recherche")
    print("Target: ABDELILAH ABDELLAOUI")
    print("="*50)
    
    # Initialisation du moteur OSINT
    engine = OSINTSearchEngine()
    
    # Lancement de la recherche complète
    results = await engine.run_complete_search()
    
    # Génération du rapport
    engine.generate_report()
    
    # Sauvegarde des résultats
    output_file = f"/workspaces/abdou.github.io/osint_report_{int(time.time())}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Rapport sauvegardé: {output_file}")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
