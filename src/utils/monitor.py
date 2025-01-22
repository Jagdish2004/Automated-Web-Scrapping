import pandas as pd
import time
from src.utils.logger import setup_logger
from typing import Dict
import os

logger = setup_logger("monitor")

class ScrapingMonitor:
    def __init__(self):
        self.last_count = 0
        self.start_time = time.time()
    
    def check_progress(self) -> Dict:
        """Check scraping progress"""
        try:
            if not os.path.exists('data/google_leads.csv'):
                return {
                    "status": "No data file found",
                    "leads": 0,
                    "rate": 0
                }
            
            df = pd.read_csv('data/google_leads.csv')
            current_count = len(df)
            elapsed_time = (time.time() - self.start_time) / 3600  # hours
            
            # Calculate scraping rate
            new_leads = current_count - self.last_count
            rate_per_hour = new_leads / elapsed_time if elapsed_time > 0 else 0
            
            self.last_count = current_count
            
            return {
                "status": "Active" if new_leads > 0 else "Idle",
                "total_leads": current_count,
                "new_leads": new_leads,
                "rate_per_hour": round(rate_per_hour, 2),
                "elapsed_hours": round(elapsed_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Error checking progress: {e}")
            return {"status": f"Error: {str(e)}"}

def monitor_scraping():
    """Monitor scraping progress"""
    monitor = ScrapingMonitor()
    
    while True:
        progress = monitor.check_progress()
        
        # Print status
        print("\n=== Scraping Status ===")
        print(f"Status: {progress['status']}")
        print(f"Total Leads: {progress.get('total_leads', 0)}")
        print(f"New Leads: {progress.get('new_leads', 0)}")
        print(f"Rate: {progress.get('rate_per_hour', 0)} leads/hour")
        print(f"Elapsed Time: {progress.get('elapsed_hours', 0)} hours")
        print("=====================\n")
        
        time.sleep(300)  # Check every 5 minutes

if __name__ == "__main__":
    monitor_scraping() 