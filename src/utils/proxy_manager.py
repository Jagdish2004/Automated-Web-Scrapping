import random
from typing import List, Dict
from src.utils.logger import setup_logger
import requests
from requests.exceptions import RequestException
import concurrent.futures
import time
from src.utils.proxy_tester import ProxyTester

class ProxyManager:
    def __init__(self):
        self.logger = setup_logger("proxy_manager")
        self.proxies = self._initialize_proxies()
        self.tester = ProxyTester()
        self.working_proxies = []
        self.current_index = 0
        self.last_test_time = 0
        self.test_interval = 300  # Test proxies every 5 minutes
        
    def _initialize_proxies(self) -> List[Dict[str, str]]:
        """Initialize list of proxy configurations"""
        proxy_list = [
    "47.251.122.81:8888",
    "91.92.155.207:3128",
    "18.223.25.15:80",
    "13.38.153.36:80",
    "13.37.89.201:80",
    "13.37.59.99:3128",
    "13.38.176.104:3128",
    "13.36.104.85:80",
    "13.36.87.105:3128",
    "15.236.106.236:3128",
    "44.218.183.55:80",
    "44.195.247.145:80",
    "102.223.186.246:8888",
    "165.232.129.150:80",
    "54.67.125.45:3128",
    "13.56.192.187:80",
    "3.136.29.104:80",
    "3.71.239.218:3128",
    "3.122.84.99:3128",
    "35.76.62.196:80",
    "35.79.120.242:3128",
    "3.127.121.101:80",
    "46.51.249.135:3128",
    "3.139.242.184:80",
    "3.21.101.158:3128",
    "3.12.144.146:3128",
    "46.47.197.210:3128",
    "204.236.176.61:3128",
    "3.129.184.210:80",
    "3.130.65.162:3128",
    "31.47.58.37:80",
    "3.212.148.199:3128",
    "39.109.113.97:4090",
    "3.141.217.225:80",
    "13.59.156.167:3128",
    "197.255.125.12:80",
    "104.207.35.29:3128",
    "104.207.36.188:3128",
    "104.207.53.152:3128",
    "156.228.92.190:3128",
    "104.207.44.51:3128",
    "156.228.90.132:3128",
    "156.228.102.192:3128",
    "104.207.51.152:3128",
    "104.239.13.95:6724",
    "156.228.85.116:3128",
    "156.228.86.22:3128",
    "156.228.90.222:3128",
    "156.228.107.110:3128",
    "156.228.118.34:3128",
    "104.207.60.129:3128",
    "104.207.53.60:3128",
    "156.228.93.8:3128",
    "104.207.32.209:3128",
    "156.228.115.76:3128",
    "156.228.119.46:3128",
    "104.207.38.234:3128",
    "156.228.99.144:3128",
    "104.207.46.61:3128",
    "104.207.36.140:3128",
    "104.207.57.235:3128",
    "156.228.86.7:3128",
    "104.207.45.96:3128",
    "156.228.87.185:3128",
    "47.243.114.192:8180",
    "3.90.100.12:80",
    "158.255.77.168:80",
    "54.248.238.110:80",
    "167.235.77.25:80",
    "47.88.59.79:82",
    "51.254.78.223:80",
    "134.209.23.180:8888",
    "43.156.148.170:59394",
    "204.236.137.68:80",
    "52.73.224.54:3128",
    "44.219.175.186:80",
    "169.56.21.242:8080",
    "216.229.112.25:8080",
    "192.73.244.36:80",
    "222.252.194.204:8080",
    "65.108.239.60:3128",
    "172.191.74.198:8080",
    "139.162.78.109:8080",
    "66.29.154.103:3128",
    "23.82.137.161:80",
    "147.75.34.92:9443",
    "123.58.199.232:8168",
    "203.115.101.55:82",
    "13.37.73.214:80",
    "50.207.199.83:80",
    "50.174.7.153:80",
    "50.169.37.50:80",
    "50.232.104.86:80",
    "50.175.212.66:80",
    "50.217.226.47:80",
    "50.239.72.16:80",
    "50.239.72.19:80",
    "190.58.248.86:80",
    "189.202.188.149:80",
    "201.148.32.162:80",
    "50.122.86.118:80",
    "103.152.112.120:80",
    "184.169.154.119:80",
    "35.209.198.222:80",
    "157.245.97.60:80",
    "23.247.136.245:80",
    "23.247.136.248:80",
    "13.208.56.180:80",
    "35.72.118.126:80",
    "3.37.125.76:3128",
    "3.123.150.192:80",
    "52.196.1.182:80",
    "158.255.77.169:80",
    "8.215.110.63:7777",
    "38.7.20.138:999",
    "200.251.41.61:8002",
    "188.132.222.56:8080",
    "203.77.215.45:10000",
    "50.168.72.116:80",
    "63.35.64.177:3128",
    "43.157.124.81:8888",
    "87.248.129.32:80",
    "178.128.113.118:23128",
    "162.223.90.130:80",
    "91.107.196.104:8585",
    "47.90.205.231:33333",
    "0.0.0.0:80",
    "97.74.87.226:80",
    "8.219.97.248:80",
    "51.89.255.67:80",
    "20.210.113.32:8123",
    "117.103.71.160:8715",
    "103.168.149.3:8181",
    "103.124.110.57:8080",
    "103.125.174.73:7777",
    "197.157.138.206:8080",
    "175.100.91.212:8080",
    "190.122.88.118:8080",
    "62.210.15.199:80",
    "47.236.231.113:8888",
]

        
        return [{"http": f"http://{proxy}", "https": f"http://{proxy}"} 
                for proxy in proxy_list]
    
    def _verify_proxy(self, proxy: Dict[str, str]) -> bool:
        """Verify if proxy is working"""
        try:
            test_url = 'https://www.google.com'
            response = requests.get(
                test_url,
                proxies=proxy,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124'}
            )
            return response.status_code == 200
        except RequestException:
            return False

    def _verify_proxies(self) -> List[Dict[str, str]]:
        """Verify and test proxies"""
        current_time = time.time()
        
        # Only test if enough time has passed
        if current_time - self.last_test_time > self.test_interval:
            self.logger.info("Testing proxies...")
            working_proxies = self.tester.test_proxy_list(self.proxies)
            self.working_proxies = [p['proxy'] for p in working_proxies]
            self.last_test_time = current_time
            
            self.logger.info(f"Found {len(self.working_proxies)} working proxies")
            
            # Save working proxies to file
            self._save_working_proxies()
            
        return self.working_proxies

    def get_random_proxy(self) -> Dict[str, str]:
        """Get a random proxy from the pool"""
        proxy = random.choice(self.proxies)
        self.logger.info(f"Selected proxy: {proxy['http']}")
        return proxy
    
    def get_next_proxy(self) -> Dict[str, str]:
        """Get next working proxy"""
        if not self.working_proxies:
            self._verify_proxies()
            
        if not self.working_proxies:
            raise Exception("No working proxies available")
            
        proxy = self.working_proxies[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.working_proxies)
        
        return {"http": proxy, "https": proxy}

    def _save_working_proxies(self):
        """Save working proxies to file"""
        with open('data/working_proxies.txt', 'w') as f:
            for proxy in self.working_proxies:
                f.write(f"{proxy}\n") 