import asyncio
import aiohttp
import json
import re
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from urllib.parse import urlparse, quote
import hashlib
import base64

# Basic imports only - AI/ML disabled for initial setup
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Web scraping
try:
    from bs4 import BeautifulSoup
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False

logger = logging.getLogger(__name__)

class OSINTEngine:
    """Advanced OSINT Engine with AI capabilities"""
    
    def __init__(self):
        self.session = None
        self.openai_client = None
        self.social_media_apis = {}
        self.setup_apis()
    
    def setup_apis(self):
        """Initialize API connections"""
        import os
        
        # OpenAI for AI analysis
        if OPENAI_AVAILABLE and os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
            self.openai_client = openai
        else:
            self.openai_client = None
        
        # Social media APIs
        self.social_media_apis = {
            'twitter': os.getenv('TWITTER_BEARER_TOKEN'),
            'linkedin': os.getenv('LINKEDIN_API_KEY'),
            'instagram': os.getenv('INSTAGRAM_API_KEY'),
        }
    
    async def get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'OSINT-AI/1.0 (https://osint-ai.com)'
                }
            )
        return self.session
    
    async def search_person(self, name: str, sources: List[str] = None, advanced_ai: bool = False) -> Dict[str, Any]:
        """Comprehensive person search using multiple OSINT sources"""
        
        if sources is None:
            sources = ["social_media", "public_records", "search_engines"]
        
        results = {
            "query": name,
            "timestamp": datetime.utcnow().isoformat(),
            "sources_searched": sources,
            "profiles_found": [],
            "social_media": {},
            "public_records": {},
            "images": [],
            "related_people": [],
            "ai_analysis": {},
            "confidence_score": 0
        }
        
        # Search social media platforms
        if "social_media" in sources:
            social_results = await self._search_social_media(name)
            results["social_media"] = social_results
            
        # Search public records
        if "public_records" in sources:
            records_results = await self._search_public_records(name)
            results["public_records"] = records_results
            
        # Search engines
        if "search_engines" in sources:
            search_results = await self._search_engines(name)
            results["search_engine_results"] = search_results
            
        # Image search and face recognition
        if "images" in sources:
            image_results = await self._search_images(name)
            results["images"] = image_results
            
        # AI-powered analysis (premium feature)
        if advanced_ai and self.openai_client:
            ai_analysis = await self._ai_analyze_person(results)
            results["ai_analysis"] = ai_analysis
            
        # Calculate overall confidence score
        results["confidence_score"] = self._calculate_confidence_score(results)
        
        return results
    
    async def search_email(self, email: str, sources: List[str] = None) -> Dict[str, Any]:
        """Search for email information across multiple sources"""
        
        results = {
            "email": email,
            "timestamp": datetime.utcnow().isoformat(),
            "is_valid": False,
            "breaches": [],
            "social_profiles": [],
            "owner_info": {},
            "domain_info": {},
            "confidence_score": 0
        }
        
        # Validate email format
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, email):
            results["error"] = "Invalid email format"
            return results
        
        results["is_valid"] = True
        domain = email.split('@')[1]
        
        # Check data breaches
        breach_results = await self._check_email_breaches(email)
        results["breaches"] = breach_results
        
        # Search for social profiles
        social_profiles = await self._search_email_social_profiles(email)
        results["social_profiles"] = social_profiles
        
        # Domain information
        domain_info = await self._get_domain_info(domain)
        results["domain_info"] = domain_info
        
        # Try to find owner information
        owner_info = await self._find_email_owner(email)
        results["owner_info"] = owner_info
        
        results["confidence_score"] = self._calculate_email_confidence(results)
        
        return results
    
    async def search_domain(self, domain: str, sources: List[str] = None) -> Dict[str, Any]:
        """Comprehensive domain investigation"""
        
        results = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "whois": {},
            "dns_records": {},
            "subdomains": [],
            "ssl_certificate": {},
            "technologies": [],
            "social_presence": {},
            "reputation": {},
            "confidence_score": 0
        }
        
        # WHOIS lookup
        whois_info = await self._get_whois_info(domain)
        results["whois"] = whois_info
        
        # DNS records
        dns_records = await self._get_dns_records(domain)
        results["dns_records"] = dns_records
        
        # Subdomain enumeration
        subdomains = await self._enumerate_subdomains(domain)
        results["subdomains"] = subdomains
        
        # SSL certificate information
        ssl_info = await self._get_ssl_info(domain)
        results["ssl_certificate"] = ssl_info
        
        # Technology detection
        technologies = await self._detect_technologies(domain)
        results["technologies"] = technologies
        
        # Social media presence
        social_presence = await self._check_domain_social_presence(domain)
        results["social_presence"] = social_presence
        
        # Domain reputation
        reputation = await self._check_domain_reputation(domain)
        results["reputation"] = reputation
        
        results["confidence_score"] = self._calculate_domain_confidence(results)
        
        return results
    
    async def _search_social_media(self, name: str) -> Dict[str, Any]:
        """Search across social media platforms"""
        
        platforms = {
            "twitter": await self._search_twitter(name),
            "linkedin": await self._search_linkedin(name),
            "facebook": await self._search_facebook(name),
            "instagram": await self._search_instagram(name),
            "tiktok": await self._search_tiktok(name),
            "youtube": await self._search_youtube(name)
        }
        
        return {platform: results for platform, results in platforms.items() if results}
    
    async def _search_twitter(self, name: str) -> List[Dict[str, Any]]:
        """Search Twitter for profiles and mentions"""
        
        if not self.social_media_apis.get('twitter'):
            return []
        
        try:
            session = await self.get_session()
            headers = {
                'Authorization': f'Bearer {self.social_media_apis["twitter"]}',
                'Content-Type': 'application/json'
            }
            
            # Search for users
            url = f'https://api.twitter.com/2/users/by?usernames={quote(name)}'
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
        
        return []
    
    async def _search_linkedin(self, name: str) -> List[Dict[str, Any]]:
        """Search LinkedIn for professional profiles"""
        
        # LinkedIn has strict API access, so we'll use web scraping approach
        try:
            # This would need to be implemented with proper authentication
            # and respect LinkedIn's terms of service
            pass
        except Exception as e:
            logger.error(f"LinkedIn search error: {e}")
        
        return []
    
    async def _search_facebook(self, name: str) -> List[Dict[str, Any]]:
        """Search Facebook (limited due to API restrictions)"""
        
        # Facebook Graph API is very restricted for OSINT
        # This would require special permissions
        return []
    
    async def _search_instagram(self, name: str) -> List[Dict[str, Any]]:
        """Search Instagram profiles"""
        
        try:
            # Instagram Basic Display API or web scraping approach
            # Implementation would go here
            pass
        except Exception as e:
            logger.error(f"Instagram search error: {e}")
        
        return []
    
    async def _search_tiktok(self, name: str) -> List[Dict[str, Any]]:
        """Search TikTok profiles"""
        
        try:
            # TikTok doesn't have a public API for this
            # Would need web scraping approach
            pass
        except Exception as e:
            logger.error(f"TikTok search error: {e}")
        
        return []
    
    async def _search_youtube(self, name: str) -> List[Dict[str, Any]]:
        """Search YouTube channels and videos"""
        
        try:
            session = await self.get_session()
            api_key = self.social_media_apis.get('youtube')
            
            if not api_key:
                return []
            
            url = f'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'q': name,
                'type': 'channel',
                'key': api_key
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                    
        except Exception as e:
            logger.error(f"YouTube search error: {e}")
        
        return []
    
    async def _search_public_records(self, name: str) -> Dict[str, Any]:
        """Search public records and databases"""
        
        # This would integrate with various public record APIs
        # Examples: court records, business registrations, etc.
        
        return {
            "court_records": [],
            "business_registrations": [],
            "property_records": [],
            "voter_records": [],
            "professional_licenses": []
        }
    
    async def _search_engines(self, name: str) -> List[Dict[str, Any]]:
        """Search using search engines"""
        
        results = []
        
        # Google search (using custom search API)
        google_results = await self._search_google(name)
        results.extend(google_results)
        
        # Bing search
        bing_results = await self._search_bing(name)
        results.extend(bing_results)
        
        return results
    
    async def _search_google(self, query: str) -> List[Dict[str, Any]]:
        """Search Google using Custom Search API"""
        
        try:
            # Google Custom Search API implementation
            api_key = self.social_media_apis.get('google_search')
            cx = self.social_media_apis.get('google_cx')
            
            if not api_key or not cx:
                return []
            
            session = await self.get_session()
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': api_key,
                'cx': cx,
                'q': query,
                'num': 10
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('items', [])
                    
        except Exception as e:
            logger.error(f"Google search error: {e}")
        
        return []
    
    async def _search_bing(self, query: str) -> List[Dict[str, Any]]:
        """Search Bing using Search API"""
        
        try:
            api_key = self.social_media_apis.get('bing_search')
            
            if not api_key:
                return []
            
            session = await self.get_session()
            url = 'https://api.bing.microsoft.com/v7.0/search'
            headers = {'Ocp-Apim-Subscription-Key': api_key}
            params = {'q': query, 'count': 10}
            
            async with session.get(url, headers=headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('webPages', {}).get('value', [])
                    
        except Exception as e:
            logger.error(f"Bing search error: {e}")
        
        return []
    
    async def _search_images(self, name: str) -> List[Dict[str, Any]]:
        """Search for images and perform face recognition"""
        
        images = []
        
        # Image search using various sources
        google_images = await self._search_google_images(name)
        images.extend(google_images)
        
        # Face recognition on found images
        if images:
            face_analysis = await self._analyze_faces_in_images(images)
            return face_analysis
        
        return []
    
    async def _search_google_images(self, query: str) -> List[str]:
        """Search Google Images"""
        
        try:
            # Google Images Custom Search
            api_key = self.social_media_apis.get('google_search')
            cx = self.social_media_apis.get('google_image_cx')
            
            if not api_key or not cx:
                return []
            
            session = await self.get_session()
            url = 'https://www.googleapis.com/customsearch/v1'
            params = {
                'key': api_key,
                'cx': cx,
                'q': query,
                'searchType': 'image',
                'num': 10
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return [item['link'] for item in data.get('items', [])]
                    
        except Exception as e:
            logger.error(f"Google Images search error: {e}")
        
        return []
    
    async def _analyze_faces_in_images(self, image_urls: List[str]) -> List[Dict[str, Any]]:
        """Analyze faces in images using face recognition"""
        
        face_data = []
        
        # Face recognition temporarily disabled - requires additional dependencies
        logger.info("Face recognition feature temporarily disabled")
        return face_data
        
        # for url in image_urls[:5]:  # Limit to first 5 images
        #     try:
        #         session = await self.get_session()
        #         async with session.get(url) as response:
        #             if response.status == 200:
        #                 image_data = await response.read()
        #                 
        #                 # Load image with PIL
        #                 # image = Image.open(io.BytesIO(image_data))
        #                 # image_array = np.array(image)
        #                 
        #                 # Find faces
        #                 # face_locations = face_recognition.face_locations(image_array)
        #                 # face_encodings = face_recognition.face_encodings(image_array, face_locations)
        #                 
        #                 # for i, encoding in enumerate(face_encodings):
        #                 #     face_data.append({
        #                 #         'image_url': url,
        #                 #         'face_index': i,
        #                 #         'location': face_locations[i],
        #                 #         'encoding': encoding.tolist(),
        #                 #         'confidence': 0.8  # Placeholder
        #                 #     })
        #                     
        #     except Exception as e:
        #         logger.error(f"Face analysis error for {url}: {e}")
        
        # return face_data
    
    async def _check_email_breaches(self, email: str) -> List[Dict[str, Any]]:
        """Check if email appears in known data breaches"""
        
        breaches = []
        
        try:
            # HaveIBeenPwned API
            session = await self.get_session()
            url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
            headers = {
                'hibp-api-key': self.social_media_apis.get('hibp_api_key', ''),
                'User-Agent': 'OSINT-AI'
            }
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    breaches = await response.json()
                    
        except Exception as e:
            logger.error(f"Breach check error: {e}")
        
        return breaches
    
    async def _search_email_social_profiles(self, email: str) -> List[Dict[str, Any]]:
        """Search for social profiles associated with email"""
        
        profiles = []
        
        # This would search various platforms that allow email-based lookups
        # Implementation depends on available APIs and methods
        
        return profiles
    
    async def _get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get domain information"""
        
        info = {}
        
        try:
            # Basic domain info
            import socket
            ip = socket.gethostbyname(domain)
            info['ip_address'] = ip
            
            # More detailed info would be gathered here
            
        except Exception as e:
            logger.error(f"Domain info error: {e}")
        
        return info
    
    async def _find_email_owner(self, email: str) -> Dict[str, Any]:
        """Try to find information about email owner"""
        
        owner_info = {}
        
        # Various techniques to find owner information
        # This is a placeholder for actual implementation
        
        return owner_info
    
    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        
        try:
            import whois
            w = whois.whois(domain)
            return w
        except Exception as e:
            logger.error(f"WHOIS error: {e}")
            return {}
    
    async def _get_dns_records(self, domain: str) -> Dict[str, Any]:
        """Get DNS records for domain"""
        
        try:
            import dns.resolver
            
            records = {}
            record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
            
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type] = [str(answer) for answer in answers]
                except:
                    pass
            
            return records
        except Exception as e:
            logger.error(f"DNS lookup error: {e}")
            return {}
    
    async def _enumerate_subdomains(self, domain: str) -> List[str]:
        """Enumerate subdomains"""
        
        subdomains = []
        
        # Common subdomain list
        common_subs = ['www', 'mail', 'ftp', 'admin', 'api', 'blog', 'shop', 'app']
        
        for sub in common_subs:
            try:
                import socket
                full_domain = f"{sub}.{domain}"
                socket.gethostbyname(full_domain)
                subdomains.append(full_domain)
            except:
                pass
        
        return subdomains
    
    async def _get_ssl_info(self, domain: str) -> Dict[str, Any]:
        """Get SSL certificate information"""
        
        try:
            import ssl
            import socket
            
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return cert
        except Exception as e:
            logger.error(f"SSL info error: {e}")
            return {}
    
    async def _detect_technologies(self, domain: str) -> List[str]:
        """Detect technologies used by website"""
        
        technologies = []
        
        try:
            session = await self.get_session()
            async with session.get(f'http://{domain}') as response:
                if response.status == 200:
                    content = await response.text()
                    headers = response.headers
                    
                    # Analyze headers and content for technology indicators
                    if 'Server' in headers:
                        technologies.append(headers['Server'])
                    
                    # Check for common frameworks/CMS
                    if 'wordpress' in content.lower():
                        technologies.append('WordPress')
                    if 'drupal' in content.lower():
                        technologies.append('Drupal')
                    # Add more detection logic
                    
        except Exception as e:
            logger.error(f"Technology detection error: {e}")
        
        return technologies
    
    async def _check_domain_social_presence(self, domain: str) -> Dict[str, Any]:
        """Check social media presence for domain"""
        
        social_presence = {}
        
        # Check if domain has social media accounts
        platforms = ['twitter', 'facebook', 'linkedin', 'instagram']
        
        for platform in platforms:
            # Implementation would check for official accounts
            social_presence[platform] = None
        
        return social_presence
    
    async def _check_domain_reputation(self, domain: str) -> Dict[str, Any]:
        """Check domain reputation across various sources"""
        
        reputation = {
            'malware_detected': False,
            'phishing_detected': False,
            'reputation_score': 50,  # Neutral
            'sources_checked': []
        }
        
        # Check various reputation sources
        # VirusTotal, Google Safe Browsing, etc.
        
        return reputation
    
    async def _ai_analyze_person(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered analysis of person search results"""
        
        if not self.openai_client:
            return {}
        
        try:
            # Prepare data for AI analysis
            analysis_prompt = f"""
            Analyze the following OSINT search results for a person and provide insights:
            
            Search Query: {search_results.get('query', '')}
            Social Media Profiles Found: {len(search_results.get('social_media', {}))}
            Public Records: {search_results.get('public_records', {})}
            
            Please provide:
            1. Risk assessment (Low/Medium/High)
            2. Notable patterns or connections
            3. Verification confidence
            4. Recommendations for further investigation
            """
            
            response = await self.openai_client.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=500
            )
            
            return {
                'ai_insights': response.choices[0].message.content,
                'risk_level': 'Medium',  # Parsed from AI response
                'confidence': 75,
                'recommendations': []
            }
            
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return {}
    
    def _calculate_confidence_score(self, results: Dict[str, Any]) -> int:
        """Calculate confidence score based on results quality"""
        
        score = 0
        
        # Add points for different types of findings
        if results.get('social_media'):
            score += 30
        if results.get('public_records'):
            score += 25
        if results.get('images'):
            score += 20
        if results.get('search_engine_results'):
            score += 15
        if results.get('ai_analysis'):
            score += 10
        
        return min(score, 100)
    
    def _calculate_email_confidence(self, results: Dict[str, Any]) -> int:
        """Calculate confidence score for email search"""
        
        score = 0
        
        if results.get('is_valid'):
            score += 20
        if results.get('breaches'):
            score += 30
        if results.get('social_profiles'):
            score += 25
        if results.get('owner_info'):
            score += 25
        
        return min(score, 100)
    
    def _calculate_domain_confidence(self, results: Dict[str, Any]) -> int:
        """Calculate confidence score for domain search"""
        
        score = 0
        
        if results.get('whois'):
            score += 25
        if results.get('dns_records'):
            score += 20
        if results.get('ssl_certificate'):
            score += 15
        if results.get('technologies'):
            score += 15
        if results.get('subdomains'):
            score += 15
        if results.get('reputation'):
            score += 10
        
        return min(score, 100)
    
    async def close(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
