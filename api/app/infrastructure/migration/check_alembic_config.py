#!/usr/bin/env python3
import os
import sys
import subprocess

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from app.infrastructure.settings.api_settings import settings

def check_alembic_config():
    print("🔍 Checking Alembic configuration...")
    
    alembic_ini_path = "app/infrastructure/migration/alembic/alembic.ini"
    if not os.path.exists(alembic_ini_path):
        print(f"❌ Not found {alembic_ini_path}")
        return False
    print(f"✅ {alembic_ini_path} found")
    
    alembic_dir_path = "app/infrastructure/migration/alembic"
    if not os.path.exists(alembic_dir_path):
        print(f"❌ Not found {alembic_dir_path}")
        return False
    print(f"✅ {alembic_dir_path} found")
    
    env_py_path = "app/infrastructure/migration/alembic/env.py"
    if not os.path.exists(env_py_path):
        print(f"❌ Not found {env_py_path}")
        return False
    print(f"✅ {env_py_path} found")
    
    print(f"\n📊 Current configuration:")
    print(f"   Database: {settings.POSTGRES_DB}")
    print(f"   Host: {settings.POSTGRES_HOST}")
    print(f"   Port: {settings.POSTGRES_PORT}")
    print(f"   Username: {settings.POSTGRES_USER}")
    print(f"   Database URL: {settings.database_url}")
    
    print(f"\n🧪 Checking connection with Alembic...")
    try:
        result = subprocess.run(
            "alembic -c app/infrastructure/migration/alembic/alembic.ini current",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ Connection with Alembic successful")
            if result.stdout.strip():
                print(f"Current migration: {result.stdout.strip()}")
            else:
                print("There are no applied migrations")
        else:
            print(f"❌ Connection error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ Timeout to connect to the database")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False
    
    print("\n✅ Alembic configuration is correct")
    return True

if __name__ == "__main__":
    success = check_alembic_config()
    sys.exit(0 if success else 1)
