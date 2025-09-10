"""
68GB Game Crawler with Cloudflare bypass
"""
import asyncio
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, Optional, List
from loguru import logger

import cloudscraper
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from config import settings, GAME_TYPES
from database import save_game_result
from services.notification_service import NotificationService

class GameCrawler:
    """Main crawler class for 68GB game data"""
    
    def __init__(self):
        self.is_running = False
        self.session = None
        self.driver = None
        self.notification_service = NotificationService()
        self.last_results = {}  # Store last results to detect changes
        
    async def start_crawling(self):
        """Start the crawling process"""
        self.is_running = True
        logger.info("Starting game crawler...")
        
        while self.is_running:
            try:
                await self._crawl_all_games()
                await asyncio.sleep(settings.CRAWL_INTERVAL)
            except Exception as e:
                logger.error(f"Error in crawling loop: {e}")
                await asyncio.sleep(settings.CRAWL_INTERVAL)
    
    async def stop_crawling(self):
        """Stop the crawling process"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
        if self.session:
            self.session.close()
        logger.info("Game crawler stopped")
    
    async def _crawl_all_games(self):
        """Crawl all supported games"""
        for game_type, game_config in GAME_TYPES.items():
            try:
                result = await self._crawl_game(game_type)
                if result:
                    await self._process_game_result(game_type, result)
            except Exception as e:
                logger.error(f"Error crawling {game_type}: {e}")
    
    async def _crawl_game(self, game_type: str) -> Optional[Dict]:
        """Crawl specific game data"""
        # Try multiple methods to bypass Cloudflare
        methods = [
            self._crawl_with_cloudscraper,
            self._crawl_with_selenium,
            self._crawl_with_undetected_chrome
        ]
        
        for method in methods:
            try:
                result = await method(game_type)
                if result:
                    logger.info(f"Successfully crawled {game_type} using {method.__name__}")
                    return result
            except Exception as e:
                logger.warning(f"Method {method.__name__} failed for {game_type}: {e}")
                continue
        
        logger.error(f"All crawling methods failed for {game_type}")
        return None
    
    async def _crawl_with_cloudscraper(self, game_type: str) -> Optional[Dict]:
        """Crawl using cloudscraper (fastest method)"""
        if not self.session:
            self.session = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )
        
        # Try to find game-specific endpoints
        endpoints_to_try = [
            f"{settings.GAME_URL}api/{game_type}",
            f"{settings.GAME_URL}game/{game_type}/results",
            f"{settings.GAME_URL}{game_type}",
            f"{settings.GAME_URL}api/game-results/{game_type}",
            settings.GAME_URL  # Fallback to main page
        ]
        
        for endpoint in endpoints_to_try:
            try:
                response = self.session.get(
                    endpoint,
                    timeout=settings.REQUEST_TIMEOUT,
                    headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                        'Accept': 'application/json, text/html, */*',
                        'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
                        'Referer': settings.GAME_URL
                    }
                )
                
                if response.status_code == 200:
                    # Try to parse as JSON first
                    try:
                        data = response.json()
                        if self._is_valid_game_data(data, game_type):
                            return data
                    except:
                        # If not JSON, parse HTML
                        html_data = self._parse_html_for_game_data(response.text, game_type)
                        if html_data:
                            return html_data
                            
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
                continue
        
        return None
    
    async def _crawl_with_selenium(self, game_type: str) -> Optional[Dict]:
        """Crawl using regular Selenium"""
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        if settings.HEADLESS_BROWSER:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        try:
            driver.get(settings.GAME_URL)
            
            # Wait for page to load and bypass Cloudflare
            WebDriverWait(driver, 30).until(
                lambda d: "Cloudflare" not in d.page_source or 
                         any(keyword in d.page_source.lower() for keyword in ["game", "tài xỉu", "bàn đỏ"])
            )
            
            # Look for game data in page
            game_data = self._extract_game_data_from_page(driver, game_type)
            return game_data
            
        finally:
            driver.quit()
    
    async def _crawl_with_undetected_chrome(self, game_type: str) -> Optional[Dict]:
        """Crawl using undetected Chrome (most reliable for Cloudflare)"""
        options = uc.ChromeOptions()
        if settings.HEADLESS_BROWSER:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = uc.Chrome(options=options)
        
        try:
            driver.get(settings.GAME_URL)
            
            # Wait for Cloudflare to pass
            time.sleep(10)  # Give time for Cloudflare check
            
            # Wait for game content to load
            WebDriverWait(driver, 30).until(
                lambda d: any(keyword in d.page_source.lower() 
                            for keyword in ["game", "tài xỉu", "bàn đỏ", "kết quả"])
            )
            
            # Extract game data
            game_data = self._extract_game_data_from_page(driver, game_type)
            return game_data
            
        finally:
            driver.quit()
    
    def _extract_game_data_from_page(self, driver, game_type: str) -> Optional[Dict]:
        """Extract game data from loaded page"""
        try:
            # Look for common game data patterns
            selectors_to_try = [
                f"[data-game='{game_type}']",
                f".{game_type}-result",
                f"#{game_type}-data",
                ".game-result",
                ".result-data",
                "[data-result]",
                ".md5-result"
            ]
            
            for selector in selectors_to_try:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.get_attribute('textContent') or element.text
                        data_attr = element.get_attribute('data-result')
                        
                        if text or data_attr:
                            # Try to parse as JSON
                            try:
                                if data_attr:
                                    data = json.loads(data_attr)
                                else:
                                    data = json.loads(text)
                                
                                if self._is_valid_game_data(data, game_type):
                                    return data
                            except:
                                # Create data from text
                                if text and any(char.isdigit() for char in text):
                                    return self._create_game_data_from_text(text, game_type)
                except:
                    continue
            
            # Fallback: look for any numeric patterns that might be results
            page_source = driver.page_source
            return self._parse_html_for_game_data(page_source, game_type)
            
        except Exception as e:
            logger.error(f"Error extracting game data: {e}")
            return None

    def _parse_html_for_game_data(self, html: str, game_type: str) -> Optional[Dict]:
        """Parse HTML content for game data"""
        from bs4 import BeautifulSoup
        import re

        soup = BeautifulSoup(html, 'html.parser')

        # Look for patterns that might contain game results
        patterns = [
            r'result["\']?\s*:\s*["\']?(\w+)',
            r'md5["\']?\s*:\s*["\']?([a-f0-9]{32})',
            r'session["\']?\s*:\s*["\']?(\w+)',
            r'"result_md5"\s*:\s*"([a-f0-9]{32})"',
            r'data-result["\']?\s*=\s*["\']([^"\']+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                # Create game data from matches
                return {
                    'game_type': game_type,
                    'result': matches[0] if matches else None,
                    'timestamp': datetime.now().isoformat(),
                    'session_id': f"{game_type}_{int(time.time())}",
                    'result_md5': self._generate_md5(str(matches[0]) if matches else str(time.time()))
                }

        return None

    def _create_game_data_from_text(self, text: str, game_type: str) -> Dict:
        """Create game data structure from text"""
        # Extract numbers and meaningful data from text
        import re
        numbers = re.findall(r'\d+', text)

        result_value = numbers[0] if numbers else str(int(time.time()) % 1000)

        return {
            'game_type': game_type,
            'result': result_value,
            'timestamp': datetime.now().isoformat(),
            'session_id': f"{game_type}_{int(time.time())}",
            'result_md5': self._generate_md5(result_value),
            'raw_text': text
        }

    def _is_valid_game_data(self, data: Dict, game_type: str) -> bool:
        """Check if data is valid game data"""
        if not isinstance(data, dict):
            return False

        # Check for required fields
        required_fields = ['result', 'timestamp']
        optional_fields = ['result_md5', 'session_id', 'game_type']

        has_required = any(field in data for field in required_fields)
        has_game_data = any(field in data for field in optional_fields)

        return has_required or has_game_data

    def _generate_md5(self, data: str) -> str:
        """Generate MD5 hash for data"""
        return hashlib.md5(data.encode()).hexdigest()

    async def _process_game_result(self, game_type: str, result_data: Dict):
        """Process and save game result"""
        try:
            # Generate session ID if not present
            session_id = result_data.get('session_id', f"{game_type}_{int(time.time())}")

            # Generate MD5 if not present
            result_md5 = result_data.get('result_md5')
            if not result_md5:
                result_str = str(result_data.get('result', '')) + str(result_data.get('timestamp', ''))
                result_md5 = self._generate_md5(result_str)

            # Check if this is a new result
            last_md5 = self.last_results.get(game_type)
            if last_md5 == result_md5:
                logger.debug(f"No new result for {game_type}")
                return

            # Save to database
            db_result = await save_game_result(
                game_type=game_type,
                session_id=session_id,
                result_md5=result_md5,
                result_data=json.dumps(result_data)
            )

            # Update last result
            self.last_results[game_type] = result_md5

            # Send notifications
            await self.notification_service.send_new_result_notification(
                game_type=game_type,
                result_data=result_data,
                result_md5=result_md5
            )

            logger.info(f"New {game_type} result saved: {result_md5}")

        except Exception as e:
            logger.error(f"Error processing game result for {game_type}: {e}")

    async def get_current_results(self) -> Dict:
        """Get current results for all games"""
        results = {}
        for game_type in GAME_TYPES.keys():
            try:
                result = await self._crawl_game(game_type)
                if result:
                    results[game_type] = result
            except Exception as e:
                logger.error(f"Error getting current result for {game_type}: {e}")
                results[game_type] = None

        return results
