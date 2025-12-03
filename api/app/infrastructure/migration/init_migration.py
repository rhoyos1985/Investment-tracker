#!/usr/bin/env python3
import os
import subprocess
import time
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))
from app.infrastructure.settings.api_settings import settings

def run_command(command, cwd=None):
    print(f"Ejecutando: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Output: {result.stdout}")
    return True

def wait_for_postgres():
    print("⏳ Waiting for PostgreSQL to be ready...")
    for number_of_try in range(10):
        if not run_command(f"pg_isready -h {settings.POSTGRES_HOST} -p {settings.POSTGRES_PORT} -U {settings.POSTGRES_USER} -d {settings.POSTGRES_DB}"): 
            print("✅ PostgreSQL está listo")
            return True
        print(f"{number_of_try+1}/20: PostgreSQL is not ready, trying...")
        time.sleep(2)
    print("❌ It was not possible to connect to PostgreSQL after 20 tries")
    return False

def main():
    print("🚀 Migration process started...")
    if not wait_for_postgres():
        return
    
    alembic_path = "app/infrastructure/migration/alembic"
    if not os.path.exists(alembic_path):
        print("📁 Initializing Alembic...")
        if not run_command(f"alembic init {alembic_path}"):
            return

    print("📝 Creating initial migration...")
    if not run_command('alembic -c app/infrastructure/migration/alembic/alembic.ini revision --autogenerate -m "Initial migration"'):
        print("⚠️  It was not possible to autogenerate the initial migration, creating an empty one...")
        if not run_command('alembic -c app/infrastructure/migration/alembic/alembic.ini revision -m "Initial migration"'):
            return
    
    print("🔄 Applying migrations...")
    if not run_command("alembic -c app/infrastructure/migration/alembic/alembic.ini upgrade head"):
        return
    
    print("✅ Migration process completed successfully")
    print(f"📊 Database is ready in: {settings.database_url}")

if __name__ == "__main__":
    main()
