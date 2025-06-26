#!/usr/bin/env python3
"""
OSINT-AI Advanced Trust Scoring & Geolocation Module
Module avancé pour l'évaluation de confiance et géolocalisation
"""

import asyncio
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import re
import hashlib
from dataclasses import dataclass
from enum import Enum

class TrustLevel(Enum):
    """Niveaux de confiance"""
    VERY_TRUSTED = (90, 100, "🟢 TRÈS FIABLE", "Personne de confiance élevée")
    TRUSTED = (75, 89, "🟢 FIABLE", "Profil cohérent et positif")
    NEUTRAL = (60, 74, "🟡 NEUTRE", "Informations limitées")
    CAUTION = (40, 59, "🟡 PRUDENCE", "Vérifications supplémentaires nécessaires")
    SUSPICIOUS = (25, 39, "🟠 MÉFIANCE", "Incohérences détectées")
    UNTRUSTED = (0, 24, "🔴 NON FIABLE", "Profil suspect ou malveillant")

@dataclass
class PersonProfile:
    """Profil complet d'une personne"""
    nom_complet: str
    emails: List[str] = None
    telephones: List[str] = None
    adresses: List[str] = None
    date_naissance: str = None
    nationalite: str = None
    profession: str = None
    entreprise: str = None
    formation: List[str] = None
    reseaux_sociaux: Dict[str, str] = None
    langues: List[str] = None
    competences: List[str] = None
    
class AdvancedOSINTAnalyzer:
    """Analyseur OSINT avancé avec scoring de confiance et géolocalisation"""
    
    def __init__(self):
        self.trust_factors = {
            "identity_coherence": 20,
            "professional_stability": 25,
            "positive_contributions": 15,
            "verified_credentials": 15,
            "online_reputation": 10,
            "geographic_consistency": 10,
            "temporal_consistency": 5
        }
        
        self.risk_factors = {
            "identity_inconsistencies": -30,
            "suspicious_activity": -35,
            "negative_reputation": -25,
            "data_breaches": -15,
            "fake_profiles": -40,
            "malicious_links": -20
        }
    
    async def analyze_comprehensive_profile(self, profile: PersonProfile) -> Dict:
        """Analyse complète d'un profil avec scoring de confiance"""
        
        print(f"🔍 Analyse complète de: {profile.nom_complet}")
        print("=" * 60)
        
        results = {
            "target": profile.nom_complet,
            "timestamp": datetime.now().isoformat(),
            "trust_score": 0,
            "trust_level": None,
            "geolocation": {},
            "digital_footprint": {},
            "risk_assessment": {},
            "recommendations": []
        }
        
        # 1. Scoring de confiance
        trust_score = await self.calculate_trust_score(profile)
        results["trust_score"] = trust_score
        results["trust_level"] = self.get_trust_level(trust_score)
        
        # 2. Géolocalisation avancée
        geolocation = await self.advanced_geolocation(profile)
        results["geolocation"] = geolocation
        
        # 3. Empreinte numérique détaillée
        digital_footprint = await self.analyze_digital_footprint(profile)
        results["digital_footprint"] = digital_footprint
        
        # 4. Évaluation des risques
        risk_assessment = await self.assess_security_risks(profile)
        results["risk_assessment"] = risk_assessment
        
        # 5. Recommandations IA
        recommendations = await self.generate_ai_recommendations(results)
        results["recommendations"] = recommendations
        
        return results
    
    async def calculate_trust_score(self, profile: PersonProfile) -> int:
        """Calcul du score de confiance basé sur l'IA"""
        
        print("🧠 Calcul du score de confiance...")
        
        base_score = 50  # Score neutre de départ
        detailed_factors = []
        
        # Facteurs positifs
        if profile.emails and len(profile.emails) > 0:
            if self.validate_email_domains(profile.emails):
                base_score += 10
                detailed_factors.append("✅ Emails avec domaines légitimes (+10)")
        
        if profile.profession and profile.entreprise:
            if await self.verify_professional_info(profile.profession, profile.entreprise):
                base_score += 15
                detailed_factors.append("✅ Informations professionnelles vérifiées (+15)")
        
        if profile.formation and len(profile.formation) > 0:
            base_score += 8
            detailed_factors.append("✅ Formation mentionnée (+8)")
        
        if profile.reseaux_sociaux and len(profile.reseaux_sociaux) > 2:
            coherence = await self.check_social_media_coherence(profile.reseaux_sociaux)
            if coherence > 0.8:
                base_score += 12
                detailed_factors.append("✅ Cohérence réseaux sociaux (+12)")
        
        # Vérification d'activité récente
        if await self.check_recent_activity(profile):
            base_score += 8
            detailed_factors.append("✅ Activité en ligne récente (+8)")
        
        # Facteurs négatifs potentiels
        if await self.check_data_breaches(profile.emails if profile.emails else []):
            base_score -= 10
            detailed_factors.append("⚠️ Présence dans fuites de données (-10)")
        
        if await self.detect_suspicious_patterns(profile):
            base_score -= 15
            detailed_factors.append("⚠️ Patterns suspects détectés (-15)")
        
        # Normalisation du score
        final_score = max(0, min(100, base_score))
        
        print(f"📊 Score calculé: {final_score}/100")
        for factor in detailed_factors:
            print(f"   {factor}")
        
        return final_score
    
    async def advanced_geolocation(self, profile: PersonProfile) -> Dict:
        """Géolocalisation avancée avec triangulation"""
        
        print("🌍 Géolocalisation avancée...")
        
        geo_data = {
            "current_location": None,
            "historical_locations": [],
            "confidence_level": 0,
            "geo_patterns": [],
            "timezone_analysis": {},
            "location_sources": []
        }
        
        # Analyse des adresses fournies
        if profile.adresses:
            for adresse in profile.adresses:
                coords = await self.geocode_address(adresse)
                if coords:
                    geo_data["historical_locations"].append({
                        "address": adresse,
                        "coordinates": coords,
                        "source": "user_provided"
                    })
        
        # Analyse des métadonnées des réseaux sociaux
        if profile.reseaux_sociaux:
            social_geo = await self.extract_social_geolocation(profile.reseaux_sociaux)
            geo_data["location_sources"].extend(social_geo)
        
        # Analyse des patterns de géolocalisation
        geo_data["geo_patterns"] = await self.analyze_geo_patterns(geo_data["historical_locations"])
        
        # Détermination de la localisation actuelle probable
        if geo_data["historical_locations"]:
            geo_data["current_location"] = await self.determine_current_location(geo_data["historical_locations"])
            geo_data["confidence_level"] = self.calculate_geo_confidence(geo_data)
        
        print(f"📍 Localisation détectée avec {geo_data['confidence_level']}% de confiance")
        
        return geo_data
    
    async def analyze_digital_footprint(self, profile: PersonProfile) -> Dict:
        """Analyse détaillée de l'empreinte numérique"""
        
        print("💻 Analyse de l'empreinte numérique...")
        
        footprint = {
            "domains_owned": [],
            "social_platforms": {},
            "professional_presence": {},
            "content_creation": [],
            "online_reputation": {},
            "digital_assets": []
        }
        
        # Recherche de domaines associés
        if profile.emails:
            domains = await self.find_associated_domains(profile.emails)
            footprint["domains_owned"] = domains
        
        # Analyse des plateformes sociales
        if profile.reseaux_sociaux:
            for platform, url in profile.reseaux_sociaux.items():
                analysis = await self.analyze_social_platform(platform, url)
                footprint["social_platforms"][platform] = analysis
        
        # Recherche de présence professionnelle
        professional = await self.search_professional_presence(profile.nom_complet)
        footprint["professional_presence"] = professional
        
        # Détection de création de contenu
        content = await self.detect_content_creation(profile.nom_complet)
        footprint["content_creation"] = content
        
        print(f"🌐 {len(footprint['domains_owned'])} domaines trouvés")
        print(f"📱 {len(footprint['social_platforms'])} plateformes analysées")
        
        return footprint
    
    async def assess_security_risks(self, profile: PersonProfile) -> Dict:
        """Évaluation des risques de sécurité"""
        
        print("🛡️ Évaluation des risques de sécurité...")
        
        risks = {
            "data_exposure": [],
            "identity_theft_risk": "low",
            "phishing_vulnerability": "low", 
            "social_engineering_risk": "medium",
            "overall_risk_level": "low",
            "mitigation_recommendations": []
        }
        
        # Vérification des fuites de données
        if profile.emails:
            breaches = await self.comprehensive_breach_check(profile.emails)
            risks["data_exposure"] = breaches
            
            if len(breaches) > 0:
                risks["identity_theft_risk"] = "medium" if len(breaches) < 3 else "high"
        
        # Analyse de la vulnérabilité au phishing
        phishing_score = await self.assess_phishing_vulnerability(profile)
        risks["phishing_vulnerability"] = phishing_score
        
        # Évaluation du risque d'ingénierie sociale
        social_eng_risk = await self.assess_social_engineering_risk(profile)
        risks["social_engineering_risk"] = social_eng_risk
        
        # Calcul du niveau de risque global
        risks["overall_risk_level"] = self.calculate_overall_risk(risks)
        
        # Génération de recommandations
        risks["mitigation_recommendations"] = await self.generate_security_recommendations(risks)
        
        print(f"⚠️ Niveau de risque global: {risks['overall_risk_level'].upper()}")
        
        return risks
    
    async def generate_ai_recommendations(self, analysis_results: Dict) -> List[str]:
        """Génération de recommandations basées sur l'IA"""
        
        recommendations = []
        trust_score = analysis_results["trust_score"]
        
        if trust_score >= 75:
            recommendations.extend([
                "✅ Profil fiable pour collaborations professionnelles",
                "✅ Recommandé pour partenariats commerciaux",
                "✅ Niveau de vérification standard suffisant"
            ])
        elif trust_score >= 60:
            recommendations.extend([
                "🟡 Vérifications supplémentaires recommandées",
                "🟡 Validation des références professionnelles conseillée",
                "🟡 Surveillance périodique suggérée"
            ])
        else:
            recommendations.extend([
                "🔴 Due diligence approfondie nécessaire",
                "🔴 Vérification d'identité obligatoire",
                "🔴 Éviter les transactions sensibles"
            ])
        
        # Recommandations basées sur la géolocalisation
        geo_confidence = analysis_results["geolocation"].get("confidence_level", 0)
        if geo_confidence < 50:
            recommendations.append("📍 Localisation incertaine - vérification géographique nécessaire")
        
        # Recommandations de sécurité
        risk_level = analysis_results["risk_assessment"].get("overall_risk_level", "low")
        if risk_level in ["medium", "high"]:
            recommendations.append("🛡️ Mesures de sécurité renforcées recommandées")
        
        return recommendations
    
    def get_trust_level(self, score: int) -> Dict:
        """Détermine le niveau de confiance basé sur le score"""
        
        for level in TrustLevel:
            min_score, max_score, label, description = level.value
            if min_score <= score <= max_score:
                return {
                    "score": score,
                    "level": level.name,
                    "label": label,
                    "description": description
                }
        
        return {
            "score": score,
            "level": "UNKNOWN",
            "label": "⚪ INDÉTERMINÉ",
            "description": "Score hors limites"
        }
    
    # Méthodes utilitaires (simulées pour la démo)
    
    def validate_email_domains(self, emails: List[str]) -> bool:
        """Valide les domaines des emails"""
        legitimate_domains = ["gmail.com", "outlook.com", "yahoo.com", "company.com"]
        return any(any(domain in email for domain in legitimate_domains) for email in emails)
    
    async def verify_professional_info(self, profession: str, entreprise: str) -> bool:
        """Vérifie les informations professionnelles"""
        # Simulation - dans un vrai cas, interroger APIs LinkedIn, etc.
        return len(profession) > 3 and len(entreprise) > 3
    
    async def check_social_media_coherence(self, reseaux: Dict) -> float:
        """Vérifie la cohérence entre les réseaux sociaux"""
        # Simulation - analyse des noms, photos, informations
        return 0.85  # 85% de cohérence
    
    async def check_recent_activity(self, profile: PersonProfile) -> bool:
        """Vérifie l'activité récente en ligne"""
        # Simulation - vérification des dernières publications
        return True
    
    async def check_data_breaches(self, emails: List[str]) -> bool:
        """Vérifie la présence dans des fuites de données"""
        # Simulation - utiliserait HaveIBeenPwned API
        return len(emails) > 0 and "test" in emails[0].lower()
    
    async def detect_suspicious_patterns(self, profile: PersonProfile) -> bool:
        """Détecte des patterns suspects"""
        # Simulation - analyse des incohérences
        return False
    
    async def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """Géocode une adresse"""
        # Simulation - utiliserait Google Maps API ou équivalent
        if "Paris" in address:
            return (48.8566, 2.3522)
        elif "Casablanca" in address:
            return (33.5731, -7.5898)
        return None
    
    async def extract_social_geolocation(self, reseaux: Dict) -> List[Dict]:
        """Extrait la géolocalisation des réseaux sociaux"""
        # Simulation
        return [{"platform": "linkedin", "location": "Paris, France", "confidence": 0.8}]
    
    async def analyze_geo_patterns(self, locations: List[Dict]) -> List[str]:
        """Analyse les patterns géographiques"""
        patterns = []
        if len(locations) > 1:
            patterns.append("Déplacements fréquents France-Maroc")
        return patterns
    
    async def determine_current_location(self, locations: List[Dict]) -> Dict:
        """Détermine la localisation actuelle probable"""
        if locations:
            return locations[-1]  # Dernière localisation connue
        return {}
    
    def calculate_geo_confidence(self, geo_data: Dict) -> int:
        """Calcule le niveau de confiance géographique"""
        sources = len(geo_data.get("location_sources", []))
        locations = len(geo_data.get("historical_locations", []))
        return min(90, (sources * 20) + (locations * 15))
    
    async def find_associated_domains(self, emails: List[str]) -> List[str]:
        """Trouve les domaines associés"""
        domains = []
        for email in emails:
            domain = email.split('@')[1] if '@' in email else None
            if domain and domain not in ["gmail.com", "outlook.com", "yahoo.com"]:
                domains.append(domain)
        return domains
    
    async def analyze_social_platform(self, platform: str, url: str) -> Dict:
        """Analyse une plateforme sociale"""
        return {
            "platform": platform,
            "url": url,
            "activity_level": "medium",
            "last_activity": "2024-06-20",
            "follower_count": "unknown"
        }
    
    async def search_professional_presence(self, nom: str) -> Dict:
        """Recherche la présence professionnelle"""
        return {
            "linkedin": "found",
            "company_websites": ["techcorp.com"],
            "professional_articles": 3
        }
    
    async def detect_content_creation(self, nom: str) -> List[Dict]:
        """Détecte la création de contenu"""
        return [
            {"type": "github_repos", "count": 15},
            {"type": "blog_posts", "count": 8},
            {"type": "stackoverflow_answers", "count": 23}
        ]
    
    async def comprehensive_breach_check(self, emails: List[str]) -> List[Dict]:
        """Vérification complète des fuites de données"""
        breaches = []
        for email in emails:
            if "test" in email.lower():  # Simulation
                breaches.append({
                    "email": email,
                    "breach": "Adobe 2013",
                    "severity": "medium"
                })
        return breaches
    
    async def assess_phishing_vulnerability(self, profile: PersonProfile) -> str:
        """Évalue la vulnérabilité au phishing"""
        # Simulation basée sur l'exposition publique
        public_info_count = sum([
            len(profile.emails or []),
            len(profile.telephones or []),
            len(profile.reseaux_sociaux or {})
        ])
        
        if public_info_count > 5:
            return "high"
        elif public_info_count > 2:
            return "medium"
        return "low"
    
    async def assess_social_engineering_risk(self, profile: PersonProfile) -> str:
        """Évalue le risque d'ingénierie sociale"""
        # Simulation basée sur les informations disponibles
        return "medium"  # Par défaut
    
    def calculate_overall_risk(self, risks: Dict) -> str:
        """Calcule le niveau de risque global"""
        risk_factors = [
            risks.get("identity_theft_risk", "low"),
            risks.get("phishing_vulnerability", "low"),
            risks.get("social_engineering_risk", "low")
        ]
        
        if "high" in risk_factors:
            return "high"
        elif "medium" in risk_factors:
            return "medium"
        return "low"
    
    async def generate_security_recommendations(self, risks: Dict) -> List[str]:
        """Génère des recommandations de sécurité"""
        recommendations = []
        
        if len(risks.get("data_exposure", [])) > 0:
            recommendations.append("🔒 Changer les mots de passe des comptes compromis")
            recommendations.append("🔐 Activer l'authentification à deux facteurs")
        
        if risks.get("phishing_vulnerability") in ["medium", "high"]:
            recommendations.append("📧 Formation anti-phishing recommandée")
        
        recommendations.append("🛡️ Surveillance continue recommandée")
        
        return recommendations

# Fonction de démonstration
async def demo_advanced_analysis():
    """Démonstration de l'analyse avancée"""
    
    # Profil exemple avec données enrichies
    profile = PersonProfile(
        nom_complet="ABDELILAH ABDELLAOUI",
        emails=["abdelilah.abdellaoui@gmail.com", "a.abdellaoui@techcorp.com"],
        telephones=["+33612345678", "+212661234567"],
        adresses=["Paris, France", "Casablanca, Maroc"],
        profession="Ingénieur Logiciel",
        entreprise="TechCorp France",
        formation=["Master Informatique - Université Paris-Saclay"],
        reseaux_sociaux={
            "linkedin": "linkedin.com/in/abdelilah-abdellaoui",
            "github": "github.com/abdou3a",
            "twitter": "@abdelilah_dev"
        },
        langues=["Français", "Arabe", "Anglais"],
        competences=["Python", "JavaScript", "AI/ML"]
    )
    
    analyzer = AdvancedOSINTAnalyzer()
    results = await analyzer.analyze_comprehensive_profile(profile)
    
    # Affichage du rapport final
    print("\n" + "="*80)
    print("🎯 RAPPORT D'ANALYSE AVANCÉE")
    print("="*80)
    
    trust_info = results["trust_level"]
    print(f"\n📊 SCORE DE CONFIANCE: {trust_info['score']}/100 {trust_info['label']}")
    print(f"💬 {trust_info['description']}")
    
    geo_info = results["geolocation"]
    print(f"\n🌍 GÉOLOCALISATION:")
    print(f"📍 Confiance: {geo_info['confidence_level']}%")
    print(f"📋 Patterns: {', '.join(geo_info['geo_patterns'])}")
    
    footprint = results["digital_footprint"]
    print(f"\n💻 EMPREINTE NUMÉRIQUE:")
    print(f"🌐 Domaines: {len(footprint['domains_owned'])}")
    print(f"📱 Plateformes: {len(footprint['social_platforms'])}")
    
    risks = results["risk_assessment"]
    print(f"\n🛡️ ÉVALUATION SÉCURITÉ:")
    print(f"⚠️ Niveau de risque: {risks['overall_risk_level'].upper()}")
    print(f"💾 Fuites de données: {len(risks['data_exposure'])}")
    
    print(f"\n💡 RECOMMANDATIONS:")
    for i, rec in enumerate(results["recommendations"], 1):
        print(f"  {i}. {rec}")
    
    print("\n" + "="*80)
    
    return results

if __name__ == "__main__":
    # Lancement de la démonstration
    asyncio.run(demo_advanced_analysis())
