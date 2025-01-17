import pandas as pd
from pathlib import Path
from src.utils.logger import setup_logger

logger = setup_logger("data_checker")

def check_data_files():
    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("Data directory does not exist!")
        return
    
    for csv_file in data_dir.glob("*_leads.csv"):
        try:
            logger.info(f"\nChecking file: {csv_file}")
            df = pd.read_csv(csv_file)
            
            logger.info(f"Number of leads: {len(df)}")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            # Check for missing values
            missing_values = df.isnull().sum()
            if missing_values.any():
                logger.warning("Missing values found:")
                for col, count in missing_values[missing_values > 0].items():
                    logger.warning(f"  {col}: {count} missing values")
            
            # Display first few rows
            logger.info("\nFirst few leads:")
            print(df.head().to_string())
            
        except Exception as e:
            logger.error(f"Error checking {csv_file}: {e}")

if __name__ == "__main__":
    check_data_files() 