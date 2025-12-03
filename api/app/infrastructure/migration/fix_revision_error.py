#!/usr/bin/env python3
import os
import subprocess
import sys

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from app.infrastructure.settings.api_settings import settings

def run_command(command, cwd=None):
    print(f"➡️  Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    if result.stdout:
        print(f"✅ Output: {result.stdout}")
    return True

def drop_alembic_version_table():
    print("🗑️  Removing alembic_version table...")
    cmd = f'psql {settings.database_url} -c "DROP TABLE IF EXISTS alembic_version;"'
    return run_command(cmd)

def stamp_head():
    print("🏷️  Updating revision head...")
    return run_command("alembic -c app/infrastructure/migration/alembic.ini stamp head")

def main():
    print("🔧 Fixing Alembic revision error...")
    print("=" * 50)
    
    # Opción 1: Eliminar la tabla alembic_version
    if drop_alembic_version_table():
        print("✅ alembic_version table deleted")
    else:
        print("❌ It was not possible to delete alembic_version table...")
        print("⚠️  Trying alternative method to drop alembic_version table...")
    
    print("\n🔧 Trying assigning head revision...")
    if stamp_head():
        print("✅ Database stamped with head revision")
    else:
        print("❌ It was not possible to stamp head revision")
        print("💡 This is normal if there no migrations have been applied yet.")

    print("\n✅ Proccess completed. Please Try applying migrations again.")

if __name__ == "__main__":
    main()
