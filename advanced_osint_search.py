#!/usr/bin/env python3
"""
OSINT Advanced Search - Recherche approfondie avec techniques réelles
Target: ABDELILAH ABDELLAOUI
"""

import requests
import json
import time
from urllib.parse import quote
import re

class RealOSINTSearch:
    """Recherche OSINT avec de vraies techniques"""
    
    def __init__(self):
        self.target = "ABDELILAH ABDELLAOUI"
        self.results = {}
        
    def search_github_users(self):
        """Recherche sur GitHub API"""
        print("🐙 Recherche GitHub...")
        try:
            url = f"https://api.github.com/search/users?q={quote(self.target)}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                users = data.get('items', [])
                
                github_profiles = []
                for user in users[:5]:  # Top 5 résultats
                    profile = {
                        'username': user.get('login'),
                        'profile_url': user.get('html_url'),
                        'avatar': user.get('avatar_url'),
                        'type': user.get('type'),
                        'public_repos': user.get('public_repos', 0)
                    }
                    github_profiles.append(profile)
                
                self.results['github'] = {
                    'found': len(github_profiles),
                    'profiles': github_profiles
                }
                print(f"✅ {len(github_profiles)} profils GitHub trouvés")
                return github_profiles
            else:
                print(f"❌ Erreur GitHub API: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Erreur GitHub: {e}")
            return []
    
    def analyze_name_linguistics(self):
        """Analyse linguistique du nom"""
        print("🔤 Analyse linguistique...")
        
        analysis = {
            'first_name': 'ABDELILAH',
            'last_name': 'ABDELLAOUI',
            'origin': {
                'likely_origin': 'Maghreb (Maroc, Algérie, Tunisie)',
                'linguistic_family': 'Arabe/Berbère',
                'religious_context': 'Musulman (Abd Allah = Serviteur de Dieu)',
                'gender': 'Masculin'
            },
            'variations': {
                'first_name_variants': [
                    'Abdelilah', 'Abd Al-Ilah', 'Abdel Ilah',
                    'عبد الإله', 'Abdelilahe'
                ],
                'last_name_variants': [
                    'Abdellaoui', 'Abd Ellaoui', 'Abdel Laoui',
                    'عبد العاوي', 'Abdelaoui'
                ]
            },
            'social_handles': [
                'abdelilah.abdellaoui', 'abdelilahabdellaoui',
                'a.abdellaoui', 'abdelilah_a', 'abdellaoui.a'
            ]
        }
        
        self.results['linguistic_analysis'] = analysis
        print("✅ Analyse linguistique terminée")
        return analysis
    
    def check_domain_variations(self):
        """Vérifie les variations de domaines"""
        print("🌐 Vérification des domaines...")
        
        base_variations = [
            'abdelilahabdellaoui',
            'a.abdellaoui',
            'abdelilah.abdellaoui',
            'abdellaoui.abdelilah'
        ]
        
        domain_results = []
        for variation in base_variations:
            domains = [
                f"{variation}.com",
                f"{variation}.org",
                f"{variation}.net",
                f"{variation}.me"
            ]
            
            for domain in domains:
                try:
                    # Test DNS simple (pas de ping pour éviter les blocages)
                    import socket
                    socket.gethostbyname(domain)
                    domain_results.append({
                        'domain': domain,
                        'status': 'exists',
                        'variation': variation
                    })
                except socket.gaierror:
                    domain_results.append({
                        'domain': domain,
                        'status': 'available',
                        'variation': variation
                    })
                except Exception as e:
                    domain_results.append({
                        'domain': domain,
                        'status': f'error: {e}',
                        'variation': variation
                    })
        
        self.results['domains'] = domain_results
        existing_domains = [d for d in domain_results if d['status'] == 'exists']
        print(f"✅ {len(existing_domains)} domaines existants trouvés sur {len(domain_results)} testés")
        return domain_results
    
    def search_professional_keywords(self):
        """Recherche avec mots-clés professionnels"""
        print("💼 Génération de mots-clés professionnels...")
        
        # Basé sur l'analyse du nom et du contexte
        professional_keywords = {
            'tech_fields': [
                'développeur', 'ingénieur', 'informatique', 'software',
                'web developer', 'programmer', 'data scientist'
            ],
            'business_fields': [
                'entrepreneur', 'manager', 'consultant', 'directeur',
                'CEO', 'founder', 'business analyst'
            ],
            'academic_fields': [
                'professeur', 'chercheur', 'PhD', 'docteur',
                'université', 'recherche', 'académique'
            ],
            'geographic_keywords': [
                'Maroc', 'Morocco', 'Casablanca', 'Rabat',
                'Algérie', 'Algeria', 'Tunisie', 'Tunisia',
                'France', 'Canada', 'Belgium'
            ]
        }
        
        # Génération de requêtes combinées
        combined_queries = []
        name = self.target
        
        for category, keywords in professional_keywords.items():
            for keyword in keywords[:3]:  # Top 3 par catégorie
                combined_queries.append(f'"{name}" {keyword}')
                combined_queries.append(f'"{name}" "{keyword}"')
        
        self.results['professional_search'] = {
            'keywords': professional_keywords,
            'generated_queries': combined_queries[:20]  # Top 20
        }
        
        print(f"✅ {len(combined_queries)} requêtes professionnelles générées")
        return professional_keywords
    
    def check_social_media_apis(self):
        """Vérification sur les APIs publiques des réseaux sociaux"""
        print("📱 Vérification APIs réseaux sociaux...")
        
        # Note: La plupart des APIs sociales nécessitent des clés
        # Voici les endpoints publics disponibles
        
        social_apis = {
            'github': {
                'endpoint': f"https://api.github.com/search/users?q={quote(self.target)}",
                'status': 'available',
                'auth_required': False
            },
            'reddit': {
                'endpoint': f"https://www.reddit.com/search.json?q={quote(self.target)}",
                'status': 'available',
                'auth_required': False
            },
            'twitter': {
                'endpoint': 'https://api.twitter.com/2/users/by/username/',
                'status': 'requires_auth',
                'auth_required': True
            },
            'linkedin': {
                'endpoint': 'https://api.linkedin.com/v2/people',
                'status': 'requires_auth',
                'auth_required': True
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
                
                social_apis['reddit']['results'] = len(posts)
                social_apis['reddit']['posts'] = [
                    {
                        'title': post['data'].get('title', ''),
                        'subreddit': post['data'].get('subreddit', ''),
                        'url': f"https://reddit.com{post['data'].get('permalink', '')}"
                    }
                    for post in posts[:5]  # Top 5
                ]
            
        except Exception as e:
            social_apis['reddit']['error'] = str(e)
        
        self.results['social_apis'] = social_apis
        print("✅ Vérification APIs terminée")
        return social_apis
    
    def generate_osint_report(self):
        """Génère le rapport OSINT final"""
        print("\n" + "="*70)
        print("🎯 RAPPORT OSINT AVANCÉ - ABDELILAH ABDELLAOUI")
        print("="*70)
        
        print(f"\n📊 RÉSUMÉ EXÉCUTIF:")
        print(f"• Cible: {self.target}")
        print(f"• Date: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"• Techniques: Google Dorking, APIs publiques, Analyse linguistique")
        
        # GitHub
        if 'github' in self.results:
            github = self.results['github']
            print(f"\n🐙 GITHUB:")
            print(f"• Profils trouvés: {github['found']}")
            for profile in github['profiles']:
                print(f"  - {profile['username']}: {profile['profile_url']}")
                print(f"    Repos publics: {profile['public_repos']}")
        
        # Analyse linguistique
        if 'linguistic_analysis' in self.results:
            ling = self.results['linguistic_analysis']
            print(f"\n🔤 ANALYSE LINGUISTIQUE:")
            print(f"• Origine probable: {ling['origin']['likely_origin']}")
            print(f"• Genre: {ling['origin']['gender']}")
            print(f"• Contexte religieux: {ling['origin']['religious_context']}")
            
            print(f"• Variations du prénom:")
            for var in ling['variations']['first_name_variants']:
                print(f"  - {var}")
            
            print(f"• Handles sociaux suggérés:")
            for handle in ling['social_handles']:
                print(f"  - {handle}")
        
        # Domaines
        if 'domains' in self.results:
            existing_domains = [d for d in self.results['domains'] if d['status'] == 'exists']
            print(f"\n🌐 DOMAINES:")
            print(f"• Domaines existants: {len(existing_domains)}")
            for domain in existing_domains:
                print(f"  - {domain['domain']} (basé sur: {domain['variation']})")
        
        # Recherche professionnelle
        if 'professional_search' in self.results:
            prof = self.results['professional_search']
            print(f"\n💼 RECHERCHE PROFESSIONNELLE:")
            print(f"• Requêtes générées: {len(prof['generated_queries'])}")
            print("• Top 5 requêtes recommandées:")
            for i, query in enumerate(prof['generated_queries'][:5], 1):
                print(f"  {i}. {query}")
        
        # APIs sociales
        if 'social_apis' in self.results:
            apis = self.results['social_apis']
            print(f"\n📱 APIS RÉSEAUX SOCIAUX:")
            
            if 'reddit' in apis and 'results' in apis['reddit']:
                print(f"• Reddit: {apis['reddit']['results']} mentions trouvées")
                if 'posts' in apis['reddit']:
                    for post in apis['reddit']['posts'][:3]:
                        print(f"  - r/{post['subreddit']}: {post['title'][:50]}...")
        
        print(f"\n⚠️ RECOMMANDATIONS:")
        print("• Utiliser les requêtes Google Dorking listées")
        print("• Vérifier manuellement les profils GitHub trouvés")
        print("• Rechercher sur LinkedIn avec les variations du nom")
        print("• Contrôler les domaines existants pour des sites personnels")
        print("• Utiliser les handles suggérés sur les réseaux sociaux")
        
        print(f"\n⚖️ LÉGAL & ÉTHIQUE:")
        print("• Toutes les données proviennent de sources publiques")
        print("• Respecter la vie privée et les conditions d'utilisation")
        print("• Usage exclusivement légal et éthique")
        
        print("\n" + "="*70)
    
    def run_complete_search(self):
        """Lance la recherche complète"""
        print("🚀 OSINT-AI Platform - Recherche Avancée")
        print(f"🎯 Target: {self.target}")
        print("="*50)
        
        self.analyze_name_linguistics()
        self.search_github_users()
        self.check_domain_variations()
        self.search_professional_keywords()
        self.check_social_media_apis()
        
        # Génération du rapport
        self.generate_osint_report()
        
        # Sauvegarde
        output_file = f"/workspaces/abdou.github.io/advanced_osint_report_{int(time.time())}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Rapport détaillé sauvegardé: {output_file}")
        return self.results

if __name__ == "__main__":
    searcher = RealOSINTSearch()
    searcher.run_complete_search()
