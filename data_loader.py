#!/usr/bin/env python3
"""
Walmart Sales Data Loader
Loads CSV files into SQLite database for analysis
"""

import pandas as pd
import sqlite3
import os
import sys
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

class WalmartDataLoader:
    def __init__(self, data_dir="data", db_name="walmart_sales.db"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / db_name
        self.conn = None
        
    def connect_db(self):
        """Create database connection"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            print(f"✓ Connected to database: {self.db_path}")
            return True
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            return False
    
    def load_csv_files(self):
        """Load all CSV files from data directory"""
        csv_files = {
            'train': 'train.csv',
            'test': 'test.csv', 
            'features': 'features.csv',
            'stores': 'stores.csv'
        }
        
        datasets = {}
        
        for table_name, filename in csv_files.items():
            file_path = self.data_dir / filename
            
            if file_path.exists():
                try:
                    print(f"Loading {filename}...")
                    df = pd.read_csv(file_path)
                    
                    # Basic data cleaning
                    if 'Date' in df.columns:
                        df['Date'] = pd.to_datetime(df['Date'])
                    
                    datasets[table_name] = df
                    print(f"✓ Loaded {filename}: {len(df):,} rows, {len(df.columns)} columns")
                    
                except Exception as e:
                    print(f"✗ Error loading {filename}: {e}")
            else:
                print(f"⚠ File not found: {filename}")
                
        return datasets
    
    def create_tables(self, datasets):
        """Create tables in SQLite database"""
        if not self.conn:
            print("✗ No database connection")
            return False
            
        try:
            cursor = self.conn.cursor()
            
            for table_name, df in datasets.items():
                # Drop table if exists
                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                # Create table from DataFrame
                df.to_sql(table_name, self.conn, index=False, if_exists='replace')
                
                # Get table info
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                print(f"✓ Created table '{table_name}' with {row_count:,} rows")
            
            self.conn.commit()
            return True
            
        except Exception as e:
            print(f"✗ Error creating tables: {e}")
            return False
    
    def create_indexes(self):
        """Create useful indexes for performance"""
        if not self.conn:
            return False
            
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_train_store ON train(Store)",
            "CREATE INDEX IF NOT EXISTS idx_train_dept ON train(Dept)", 
            "CREATE INDEX IF NOT EXISTS idx_train_date ON train(Date)",
            "CREATE INDEX IF NOT EXISTS idx_train_store_dept ON train(Store, Dept)",
            "CREATE INDEX IF NOT EXISTS idx_features_store ON features(Store)",
            "CREATE INDEX IF NOT EXISTS idx_features_date ON features(Date)",
            "CREATE INDEX IF NOT EXISTS idx_stores_type ON stores(Type)"
        ]
        
        try:
            cursor = self.conn.cursor()
            for index_sql in indexes:
                cursor.execute(index_sql)
                
            self.conn.commit()
            print("✓ Created database indexes")
            return True
            
        except Exception as e:
            print(f"✗ Error creating indexes: {e}")
            return False
    
    def run_basic_queries(self):
        """Run basic validation queries"""
        if not self.conn:
            return False
            
        queries = [
            ("Total records in train", "SELECT COUNT(*) FROM train"),
            ("Unique stores", "SELECT COUNT(DISTINCT Store) FROM train"),
            ("Unique departments", "SELECT COUNT(DISTINCT Dept) FROM train"),
            ("Date range", "SELECT MIN(Date), MAX(Date) FROM train"),
            ("Total sales", "SELECT ROUND(SUM(Weekly_Sales), 2) FROM train")
        ]
        
        try:
            cursor = self.conn.cursor()
            print("\n" + "="*50)
            print("DATABASE VALIDATION")
            print("="*50)
            
            for description, query in queries:
                cursor.execute(query)
                result = cursor.fetchone()
                print(f"{description:.<30} {result[0]}")
                
            return True
            
        except Exception as e:
            print(f"✗ Error running validation queries: {e}")
            return False
    
    def get_table_info(self):
        """Get information about all tables"""
        if not self.conn:
            return False
            
        try:
            cursor = self.conn.cursor()
            
            # Get list of tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            print("\n" + "="*50)
            print("TABLE INFORMATION")
            print("="*50)
            
            for (table_name,) in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                print(f"\nTable: {table_name}")
                print(f"Rows: {row_count:,}")
                print("Columns:")
                for col in columns:
                    col_name, col_type = col[1], col[2]
                    print(f"  - {col_name} ({col_type})")
                    
            return True
            
        except Exception as e:
            print(f"✗ Error getting table info: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")

def main():
    """Main function to load data"""
    print("Walmart Sales Data Loader")
    print("="*50)
    
    # Create data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Initialize loader
    loader = WalmartDataLoader()
    
    # Connect to database
    if not loader.connect_db():
        sys.exit(1)
    
    # Load CSV files
    datasets = loader.load_csv_files()
    
    if not datasets:
        print("✗ No datasets loaded. Please ensure CSV files are in the data/ directory")
        print("\nRequired files:")
        print("  - train.csv")
        print("  - test.csv") 
        print("  - features.csv")
        print("  - stores.csv")
        print("\nDownload from: https://www.kaggle.com/c/walmart-recruiting-store-sales-forecasting/data")
        loader.close()
        sys.exit(1)
    
    # Create tables
    if not loader.create_tables(datasets):
        loader.close()
        sys.exit(1)
    
    # Create indexes
    loader.create_indexes()
    
    # Run validation
    loader.run_basic_queries()
    
    # Get table info
    loader.get_table_info()
    
    print("\n" + "="*50)
    print("✓ DATA LOADING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"Database created: {loader.db_path}")
    print("You can now run SQL queries against the database.")
    
    # Close connection
    loader.close()

if __name__ == "__main__":
    main()
