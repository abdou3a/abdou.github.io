#!/usr/bin/env python3
"""
OSINT Advanced Search - A4CH3R
Recherche approfondie avec techniques spécialisées pour pseudonymes/handles
"""

import asyncio
import requests
import json
import time
import re
from datetime import datetime
from urllib.parse import quote
import hashlib

class A4CH3R_OSINTSearch:
    """Recherche OSINT spécialisée pour A4CH3R"""
    
    def __init__(self):
        self.target = "A4CH3R"
        self.results = {
            "metadata": {
                "target": self.target,
                "search_date": datetime.now().isoformat(),
                "target_type": "handle/pseudonym",
                "confidence_analysis": {}
            },
            "platforms": {},
            "digital_footprint": {},
            "ai_analysis": {},
            "security_assessment": {}
        }
    
    async def analyze_handle_pattern(self):
        """Analyse du pattern du handle A4CH3R"""
        print("🔤 Analyse du pattern du handle...")
        
        pattern_analysis = {
            "original": "A4CH3R",
            "type": "leetspeak/gamertag",
            "meaning": "ARCHER (tireur à l'arc)",
            "character_substitution": {
                "A": "A",
                "4": "A", 
                "C": "C",
                "H": "H",
                "3": "E",
                "R": "R"
            },
            "decoded": "ARCHER",
            "cultural_context": {
                "gaming": "Handle typique des jeux vidéo",
                "hacking": "Possible référence à la culture hacker",
                "anonymity": "Pseudonyme pour préserver l'anonymat"
            },
            "variations": [
                "A4CH3R", "ARCHER", "4rch3r", "Arch3r", 
                "a4ch3r", "archer", "4RCHER", "AR4H3R"
            ],
            "probability_fields": {
                "gaming": 85,
                "cybersecurity": 70,
                "development": 60,
                "anonymous_forums": 80
            }
        }
        
        self.results["ai_analysis"]["pattern"] = pattern_analysis
        print("✅ Pattern analysé: ARCHER (leetspeak)")
        return pattern_analysis
    
    async def search_github_advanced(self):
        """Recherche GitHub avancée"""
        print("🐙 Recherche GitHub avancée...")
        
        variations = ["A4CH3R", "ARCHER", "4rch3r", "Arch3r", "a4ch3r"]
        github_results = []
        
        for variation in variations:
            try:
                # Recherche utilisateurs
                url = f"https://api.github.com/search/users?q={quote(variation)}"
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    users = data.get('items', [])
                    
                    for user in users[:3]:  # Top 3 par variation
                        # Obtenir des détails supplémentaires
                        user_url = f"https://api.github.com/users/{user['login']}"
                        user_response = requests.get(user_url, timeout=5)
                        
                        if user_response.status_code == 200:
                            user_data = user_response.json()
                            
                            profile = {
                                'username': user['login'],
                                'profile_url': user['html_url'],
                                'avatar': user['avatar_url'],
                                'public_repos': user_data.get('public_repos', 0),
                                'followers': user_data.get('followers', 0),
                                'following': user_data.get('following', 0),
                                'created_at': user_data.get('created_at'),
                                'bio': user_data.get('bio'),
                                'location': user_data.get('location'),
                                'blog': user_data.get('blog'),
                                'company': user_data.get('company'),
                                'email': user_data.get('email'),
                                'twitter_username': user_data.get('twitter_username'),
                                'match_variation': variation,
                                'confidence_score': self._calculate_username_confidence(user['login'], variation)
                            }
                            github_results.append(profile)
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"❌ Erreur GitHub pour {variation}: {e}")
        
        # Trier par score de confiance
        github_results.sort(key=lambda x: x['confidence_score'], reverse=True)
        
        self.results["platforms"]["github"] = {
            "found": len(github_results),
            "profiles": github_results[:10]  # Top 10
        }
        
        print(f"✅ {len(github_results)} profils GitHub trouvés")
        return github_results
    
    def _calculate_username_confidence(self, username, target_variation):
        """Calcule le score de confiance pour un nom d'utilisateur"""
        username_lower = username.lower()
        target_lower = target_variation.lower()
        
        # Score de base sur similarité exacte
        if username_lower == target_lower:
            return 95
        
        # Score sur inclusion
        if target_lower in username_lower or username_lower in target_lower:
            return 80
        
        # Score sur caractères communs
        common_chars = set(username_lower) & set(target_lower)
        char_score = (len(common_chars) / max(len(username_lower), len(target_lower))) * 100
        
        # Score sur pattern leetspeak
        leetspeak_score = 0
        if '4' in username_lower and 'a' in target_lower:
            leetspeak_score += 10
        if '3' in username_lower and 'e' in target_lower:
            leetspeak_score += 10
        if '1' in username_lower and ('i' in target_lower or 'l' in target_lower):
            leetspeak_score += 10
        
        return min(95, char_score + leetspeak_score)
    
    async def search_social_platforms(self):
        """Recherche sur les plateformes sociales"""
        print("📱 Recherche plateformes sociales...")
        
        social_platforms = {
            "twitter": {
                "search_url": f"https://twitter.com/search?q={quote(self.target)}",
                "profile_urls": [
                    f"https://twitter.com/{self.target}",
                    f"https://twitter.com/A4CH3R",
                    f"https://twitter.com/archer"
                ]
            },
            "instagram": {
                "search_url": f"https://www.instagram.com/explore/tags/{self.target.lower()}/",
                "profile_urls": [
                    f"https://www.instagram.com/{self.target.lower()}/",
                    f"https://www.instagram.com/a4ch3r/",
                    f"https://www.instagram.com/archer/"
                ]
            },
            "discord": {
                "note": "Handle probablement utilisé sur Discord",
                "search_methods": [
                    "Discord user search",
                    "Server member lists",
                    "Public Discord bots"
                ]
            },
            "reddit": {
                "search_url": f"https://www.reddit.com/search?q={quote(self.target)}",
                "profile_urls": [
                    f"https://www.reddit.com/user/{self.target}",
                    f"https://www.reddit.com/user/A4CH3R",
                    f"https://www.reddit.com/user/archer"
                ]
            },
            "gaming_platforms": {
                "steam": f"https://steamcommunity.com/search/users/#text={quote(self.target)}",
                "xbox": f"Xbox Live gamertag search: {self.target}",
                "psn": f"PlayStation Network search: {self.target}",
                "twitch": f"https://www.twitch.tv/{self.target.lower()}"
            }
        }
        
        # Test Reddit API
        try:
            reddit_url = f"https://www.reddit.com/search.json?q={quote(self.target)}"
            response = requests.get(reddit_url, 
                                  headers={'User-Agent': 'OSINT-Research-Bot/1.0'},
                                  timeout=10)
            
            if response.status_code == 200:
                reddit_data = response.json()
                posts = reddit_data.get('data', {}).get('children', [])
                
                social_platforms['reddit']['results'] = {
                    'posts_found': len(posts),
                    'recent_posts': [
                        {
                            'title': post['data'].get('title', ''),
                            'subreddit': post['data'].get('subreddit', ''),
                            'url': f"https://reddit.com{post['data'].get('permalink', '')}",
                            'score': post['data'].get('score', 0),
                            'created': post['data'].get('created_utc', 0)
                        }
                        for post in posts[:5]
                    ]
                }
        except Exception as e:
            social_platforms['reddit']['error'] = str(e)
        
        self.results["platforms"]["social_media"] = social_platforms
        print("✅ Plateformes sociales analysées")
        return social_platforms
    
    async def check_domain_variations(self):
        """Vérification des domaines et variations"""
        print("🌐 Vérification domaines et variations...")
        
        base_variations = [
            "a4ch3r", "archer", "4rch3r", "arch3r"
        ]
        
        domain_results = []
        for variation in base_variations:
            domains = [
                f"{variation}.com",
                f"{variation}.net", 
                f"{variation}.org",
                f"{variation}.me",
                f"{variation}.io",
                f"{variation}.dev",
                f"{variation}.gg",  # Gaming
                f"{variation}.tv"   # Streaming
            ]
            
            for domain in domains:
                try:
                    import socket
                    socket.gethostbyname(domain)
                    domain_results.append({
                        'domain': domain,
                        'status': 'exists',
                        'variation': variation,
                        'category': self._categorize_domain(domain)
                    })
                except socket.gaierror:
                    domain_results.append({
                        'domain': domain,
                        'status': 'available',
                        'variation': variation,
                        'category': self._categorize_domain(domain)
                    })
                except Exception as e:
                    domain_results.append({
                        'domain': domain,
                        'status': f'error: {e}',
                        'variation': variation,
                        'category': 'unknown'
                    })
        
        self.results["digital_footprint"]["domains"] = domain_results
        existing_domains = [d for d in domain_results if d['status'] == 'exists']
        print(f"✅ {len(existing_domains)} domaines existants sur {len(domain_results)} testés")
        return domain_results
    
    def _categorize_domain(self, domain):
        """Catégorise un domaine selon son extension"""
        if domain.endswith('.gg') or domain.endswith('.tv'):
            return 'gaming/streaming'
        elif domain.endswith('.dev') or domain.endswith('.io'):
            return 'development'
        elif domain.endswith('.com') or domain.endswith('.net'):
            return 'general'
        elif domain.endswith('.org'):
            return 'organization'
        else:
            return 'other'
    
    async def analyze_hacker_culture(self):
        """Analyse des liens avec la culture hacker/cybersec"""
        print("🛡️ Analyse culture hacker/cybersec...")
        
        hacker_analysis = {
            "leetspeak_usage": {
                "present": True,
                "score": 85,
                "indicators": ["4 for A", "3 for E", "numeric substitution"]
            },
            "potential_platforms": {
                "hackthebox": f"https://app.hackthebox.com/users/{self.target}",
                "tryhackme": f"https://tryhackme.com/p/{self.target}",
                "github_security": "Security-related repositories",
                "bugbounty": "Bug bounty platforms",
                "ctf_platforms": "Capture The Flag competitions"
            },
            "forum_searches": {
                "reddit_netsec": "/r/netsec, /r/cybersecurity",
                "stackoverflow": "Security questions and answers",
                "discord_servers": "Cybersecurity Discord servers"
            },
            "risk_assessment": {
                "anonymity_level": "High (pseudonym usage)",
                "technical_level": "Possibly advanced (handle pattern)",
                "activity_type": "Unknown - requires investigation"
            }
        }
        
        self.results["security_assessment"]["hacker_culture"] = hacker_analysis
        print("✅ Analyse cybersec terminée")
        return hacker_analysis
    
    async def generate_confidence_score(self):
        """Génère un score de confiance global"""
        print("🎯 Génération du score de confiance...")
        
        confidence_factors = {
            "pattern_consistency": 85,  # Pattern leetspeak cohérent
            "platform_presence": 0,    # À déterminer selon résultats
            "information_quality": 0,  # À déterminer selon données trouvées
            "activity_timeline": 0,    # À déterminer selon historique
            "cross_platform_validation": 0  # À déterminer selon recoupements
        }
        
        # Calcul basé sur les résultats GitHub
        github_data = self.results.get("platforms", {}).get("github", {})
        if github_data.get("found", 0) > 0:
            confidence_factors["platform_presence"] = min(80, github_data["found"] * 20)
        
        # Score global
        overall_score = sum(confidence_factors.values()) / len(confidence_factors)
        
        trust_assessment = {
            "overall_confidence": round(overall_score, 1),
            "factors": confidence_factors,
            "trust_level": self._categorize_trust(overall_score),
            "recommendations": self._generate_trust_recommendations(overall_score),
            "red_flags": [],
            "green_flags": []
        }
        
        # Analyse des red/green flags
        if overall_score > 70:
            trust_assessment["green_flags"].extend([
                "Pattern de pseudonyme cohérent",
                "Présence sur plateformes légitimes"
            ])
        
        if overall_score < 40:
            trust_assessment["red_flags"].extend([
                "Faible empreinte numérique",
                "Possibles intentions d'anonymat"
            ])
        
        self.results["ai_analysis"]["trust_assessment"] = trust_assessment
        print(f"✅ Score de confiance: {overall_score:.1f}%")
        return trust_assessment
    
    def _categorize_trust(self, score):
        """Catégorise le niveau de confiance"""
        if score >= 80:
            return "High Trust"
        elif score >= 60:
            return "Medium Trust"
        elif score >= 40:
            return "Low Trust"
        else:
            return "Very Low Trust / Suspicious"
    
    def _generate_trust_recommendations(self, score):
        """Génère des recommandations basées sur le score"""
        if score >= 80:
            return ["Profil probablement légitime", "Vérification de routine suffisante"]
        elif score >= 60:
            return ["Vérifications supplémentaires recommandées", "Surveillance modérée"]
        elif score >= 40:
            return ["Enquête approfondie nécessaire", "Validation de l'identité requise"]
        else:
            return ["Investigation complète requise", "Possibles intentions malveillantes", "Surveillance étroite"]
    
    async def search_gaming_platforms(self):
        """Recherche sur les plateformes de gaming"""
        print("🎮 Recherche plateformes gaming...")
        
        gaming_platforms = {
            "steam": {
                "search_url": f"https://steamcommunity.com/search/users/#text={quote(self.target)}",
                "note": "Handle typique pour Steam"
            },
            "discord": {
                "likelihood": "Very High",
                "note": "A4CH3R est un pattern typique Discord",
                "search_methods": ["Server searches", "Bot commands", "User directory"]
            },
            "twitch": {
                "profile_url": f"https://www.twitch.tv/{self.target.lower()}",
                "alternative_urls": [
                    "https://www.twitch.tv/a4ch3r",
                    "https://www.twitch.tv/archer"
                ]
            },
            "xbox_live": {
                "gamertag_probability": "High",
                "note": "Format compatible Xbox Live"
            },
            "playstation": {
                "psn_probability": "Medium",
                "note": "Possible PSN ID"
            },
            "esports_platforms": {
                "faceit": f"https://www.faceit.com/en/players/{self.target}",
                "esea": "ESEA profile search",
                "battlenet": "Battle.net tag possibility"
            }
        }
        
        self.results["platforms"]["gaming"] = gaming_platforms
        print("✅ Plateformes gaming analysées")
        return gaming_platforms
    
    def generate_final_report(self):
        """Génère le rapport final"""
        print("\n" + "="*70)
        print("🎯 RAPPORT OSINT COMPLET - A4CH3R")
        print("="*70)
        
        print(f"\n📊 RÉSUMÉ EXÉCUTIF:")
        print(f"• Cible: {self.target}")
        print(f"• Type: Handle/Pseudonyme (Leetspeak)")
        print(f"• Signification décodée: ARCHER")
        print(f"• Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Pattern Analysis
        pattern = self.results.get("ai_analysis", {}).get("pattern", {})
        print(f"\n🔤 ANALYSE DU PATTERN:")
        print(f"• Type: {pattern.get('type', 'N/A')}")
        print(f"• Décodage: {pattern.get('decoded', 'N/A')}")
        print(f"• Contexte: Gaming/Hacking culture")
        
        # GitHub Results
        github = self.results.get("platforms", {}).get("github", {})
        print(f"\n🐙 GITHUB INTELLIGENCE:")
        print(f"• Profils trouvés: {github.get('found', 0)}")
        
        if github.get("profiles"):
            print("• Top profils:")
            for profile in github["profiles"][:3]:
                print(f"  - {profile['username']}: {profile['profile_url']}")
                print(f"    Confiance: {profile['confidence_score']:.1f}% | Repos: {profile['public_repos']}")
                if profile.get('location'):
                    print(f"    Localisation: {profile['location']}")
        
        # Domains
        domains = self.results.get("digital_footprint", {}).get("domains", [])
        existing_domains = [d for d in domains if d['status'] == 'exists']
        print(f"\n🌐 EMPREINTE NUMÉRIQUE:")
        print(f"• Domaines existants: {len(existing_domains)}")
        for domain in existing_domains:
            print(f"  - {domain['domain']} ({domain['category']})")
        
        # Trust Assessment
        trust = self.results.get("ai_analysis", {}).get("trust_assessment", {})
        print(f"\n🛡️ ÉVALUATION DE CONFIANCE:")
        print(f"• Score global: {trust.get('overall_confidence', 0):.1f}%")
        print(f"• Niveau: {trust.get('trust_level', 'Unknown')}")
        
        if trust.get('green_flags'):
            print(f"• ✅ Points positifs:")
            for flag in trust['green_flags']:
                print(f"  - {flag}")
        
        if trust.get('red_flags'):
            print(f"• ⚠️ Points d'attention:")
            for flag in trust['red_flags']:
                print(f"  - {flag}")
        
        # Recommendations
        if trust.get('recommendations'):
            print(f"• 📋 Recommandations:")
            for rec in trust['recommendations']:
                print(f"  - {rec}")
        
        # Gaming Analysis
        gaming = self.results.get("platforms", {}).get("gaming", {})
        print(f"\n🎮 ANALYSE GAMING:")
        print(f"• Discord: {gaming.get('discord', {}).get('likelihood', 'Unknown')} probability")
        print(f"• Steam: Profile search available")
        print(f"• Gaming pattern: Highly compatible")
        
        # Security Analysis
        security = self.results.get("security_assessment", {}).get("hacker_culture", {})
        print(f"\n🔒 ANALYSE SÉCURITÉ:")
        print(f"• Leetspeak: {security.get('leetspeak_usage', {}).get('present', False)}")
        print(f"• Score technique: {security.get('leetspeak_usage', {}).get('score', 0)}%")
        print(f"• Niveau anonymat: {security.get('risk_assessment', {}).get('anonymity_level', 'Unknown')}")
        
        print(f"\n⚠️ CONCLUSION:")
        overall_score = trust.get('overall_confidence', 0)
        if overall_score >= 70:
            print("✅ PROFIL PROBABLEMENT LÉGITIME")
            print("• Handle gaming/tech standard")
            print("• Présence sur plateformes légitimes")
            print("• Risque faible")
        elif overall_score >= 40:
            print("🟡 PROFIL À SURVEILLER")
            print("• Investigation supplémentaire recommandée")
            print("• Vérification de l'activité nécessaire")
        else:
            print("🔴 PROFIL SUSPICIEUX")
            print("• Investigation approfondie requise")
            print("• Possibles intentions d'anonymat")
            print("• Surveillance étroite recommandée")
        
        print(f"\n⚖️ LÉGAL & ÉTHIQUE:")
        print("• Toutes données de sources publiques")
        print("• Respect vie privée et lois")
        print("• Usage légal uniquement")
        
        print("\n" + "="*70)
    
    async def run_complete_search(self):
        """Lance la recherche complète"""
        print("🚀 OSINT-AI Platform - Recherche A4CH3R")
        print("="*50)
        
        await self.analyze_handle_pattern()
        await self.search_github_advanced()
        await self.search_social_platforms()
        await self.check_domain_variations()
        await self.analyze_hacker_culture()
        await self.search_gaming_platforms()
        await self.generate_confidence_score()
        
        # Génération du rapport
        self.generate_final_report()
        
        # Sauvegarde
        output_file = f"/workspaces/abdou.github.io/a4ch3r_osint_report_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport détaillé sauvegardé: {output_file}")
        return self.results

if __name__ == "__main__":
    async def main():
        searcher = A4CH3R_OSINTSearch()
        await searcher.run_complete_search()
    
    asyncio.run(main())
