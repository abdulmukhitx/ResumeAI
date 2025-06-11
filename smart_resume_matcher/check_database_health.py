#!/usr/bin/env python
"""
Database health check and lock resolution script for SQLite
"""
import os
import sys
import time
import sqlite3
from pathlib import Path

# Setup Django environment
project_dir = Path(__file__).resolve().parent
sys.path.append(str(project_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
from django.conf import settings

def check_database_locks():
    """Check if the database is locked and try to resolve it"""
    db_path = settings.DATABASES['default']['NAME']
    
    print(f"Checking database: {db_path}")
    
    # Check if database file exists
    if not os.path.exists(db_path):
        print("❌ Database file does not exist!")
        return False
    
    # Check for lock files
    lock_files = [
        f"{db_path}-wal",
        f"{db_path}-shm", 
        f"{db_path}-journal"
    ]
    
    print("\nChecking for lock files:")
    for lock_file in lock_files:
        if os.path.exists(lock_file):
            size = os.path.getsize(lock_file)
            print(f"  ⚠️  {lock_file} exists (size: {size} bytes)")
        else:
            print(f"  ✅ {lock_file} does not exist")
    
    # Test database connectivity
    print("\nTesting database connectivity...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table';")
            table_count = cursor.fetchone()[0]
            print(f"✅ Database accessible - {table_count} tables found")
            
            # Test a simple query
            cursor.execute("SELECT COUNT(*) FROM accounts_user;")
            user_count = cursor.fetchone()[0]
            print(f"✅ User table accessible - {user_count} users found")
            
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def fix_database_locks():
    """Try to fix database locks"""
    print("\n🔧 Attempting to fix database locks...")
    
    db_path = settings.DATABASES['default']['NAME']
    
    # Try to connect directly with SQLite
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        
        # Enable WAL mode for better concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA synchronous=NORMAL;")
        conn.execute("PRAGMA cache_size=10000;")
        conn.execute("PRAGMA temp_store=MEMORY;")
        
        # Test the connection
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sqlite_master;")
        result = cursor.fetchone()
        
        conn.close()
        
        print(f"✅ Direct SQLite connection successful")
        print("✅ Database configuration updated for better concurrency")
        return True
        
    except sqlite3.OperationalError as e:
        if "database is locked" in str(e):
            print(f"❌ Database is still locked: {e}")
            print("🔧 Trying to force unlock...")
            
            # Try to remove lock files (dangerous, but sometimes necessary)
            lock_files = [f"{db_path}-wal", f"{db_path}-shm", f"{db_path}-journal"]
            for lock_file in lock_files:
                if os.path.exists(lock_file):
                    try:
                        os.remove(lock_file)
                        print(f"✅ Removed lock file: {lock_file}")
                    except Exception as e:
                        print(f"❌ Could not remove {lock_file}: {e}")
            
            # Try connecting again
            try:
                conn = sqlite3.connect(db_path, timeout=30)
                conn.execute("PRAGMA journal_mode=WAL;")
                conn.close()
                print("✅ Database unlocked successfully")
                return True
            except Exception as e:
                print(f"❌ Still cannot access database: {e}")
                return False
        else:
            print(f"❌ SQLite error: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    print("🔍 SQLite Database Health Check")
    print("=" * 50)
    
    # Check current status
    is_healthy = check_database_locks()
    
    if not is_healthy:
        print("\n🚨 Database issues detected, attempting to fix...")
        fixed = fix_database_locks()
        
        if fixed:
            print("\n✅ Database issues resolved!")
            # Test again
            print("\n🔍 Re-testing database...")
            check_database_locks()
        else:
            print("\n❌ Could not resolve database issues")
            print("\nPossible solutions:")
            print("1. Stop all Django processes: pkill -f 'manage.py'")
            print("2. Restart the Django server")
            print("3. Check if any other processes are using the database")
    else:
        print("\n✅ Database is healthy!")

if __name__ == "__main__":
    main()
