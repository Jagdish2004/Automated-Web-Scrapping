import requests
import concurrent.futures
from typing import Dict, List
from src.utils.logger import setup_logger
import time

logger = setup_logger("proxy_tester")

class ProxyTester:
    def __init__(self):
        self.test_urls = [
            'https://www.google.com',
            'https://www.bing.com',
            'https://www.amazon.com'
        ]
        self.timeout = 10
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
        }

    def test_proxy(self, proxy: Dict[str, str]) -> Dict:
        """Test a single proxy"""
        results = {
            'proxy': proxy['http'],
            'working': False,
            'speed': 0,
            'errors': []
        }
        
        try:
            start_time = time.time()
            response = requests.get(
                'https://www.google.com',
                proxies=proxy,
                timeout=self.timeout,
                headers=self.headers
            )
            elapsed = time.time() - start_time
            
            if response.status_code == 200:
                results['working'] = True
                results['speed'] = round(elapsed, 2)
                logger.info(f"Proxy {proxy['http']} working - Speed: {results['speed']}s")
            else:
                results['errors'].append(f"Status code: {response.status_code}")
                
        except Exception as e:
            results['errors'].append(str(e))
            logger.warning(f"Proxy {proxy['http']} failed: {str(e)}")
            
        return results

    def test_proxy_list(self, proxies: List[Dict[str, str]]) -> List[Dict]:
        """Test multiple proxies in parallel"""
        working_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_proxy = {
                executor.submit(self.test_proxy, proxy): proxy 
                for proxy in proxies
            }
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                result = future.result()
                if result['working']:
                    working_proxies.append(result)
                    
        return working_proxies 