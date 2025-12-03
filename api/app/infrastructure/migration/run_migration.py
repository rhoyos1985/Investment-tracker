#!/usr/bin/env python3
import os
import argparse
import sys
import tempfile

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from app.infrastructure.migration.alembic.util.enums import MigrationAction
from app.infrastructure.migration.cmd_process import run_shell_command

ALEMBIC_COMMAND = "alembic -c app/infrastructure/migration/alembic/alembic.ini"

def check_pending_migrations():
    print("🔍 Checking for pending Alembic migrations")
    command = f"{ALEMBIC_COMMAND} heads"
    finished_ok, output = run_shell_command(command)
    if not finished_ok:
        return MigrationAction.ERROR
    if "No head" in output:
        print("ℹ️  No migrations found.")
        return MigrationAction.NOTMIGRATIONAPPLIED
    command = f"{ALEMBIC_COMMAND} current"
    finished_ok, current_output = run_shell_command(command)
    if not finished_ok:
        return MigrationAction.ERROR
    if current_output.strip() == "":
        print("ℹ️  No migrations have been applied yet.")
        return MigrationAction.NOTMIGRATIONAPPLIED
    if current_output.strip() not in output:
        print("🚨 Pending migrations detected!")
        return MigrationAction.PENDING
    print("✅ No pending migrations.")
    return MigrationAction.NOTPENDING

def check_model_change():
    print("🔍 Checking model changes for Alembic migrations")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
        temp_path = temp_file.name
    
    try:
        command = f'{ALEMBIC_COMMAND} revision --autogenerate -m "temp_check"'
        finished_ok,_ = run_shell_command(command)
        if not finished_ok:
            return False
        
        versions_dir = "app/infrastructure/migration/alembic/versions"
        if not os.path.exists(versions_dir):
            print(f"❌ Versions directory not found: {versions_dir}")
            return False
        
        files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and 'temp_check' in f]
        
        if not files:
            print("ℹ️  No changes detected in models.")
            return False
        
        latest_file = sorted(files)[-1]
        file_path = os.path.join(versions_dir, latest_file)
                    
                    
        with open(file_path, 'r') as f:
            content = f.read()
            lines = content.split('\n')
            in_upgrade = False
            upgrade_content = []
                        
            for line in lines:
                if 'def upgrade():' in line:
                    in_upgrade = True
                    continue
                elif 'def downgrade():' in line:
                    in_upgrade = False
                    break
                elif in_upgrade and line.strip() and not line.strip().startswith('#') and 'pass' not in line:
                    upgrade_content.append(line)
           
            if upgrade_content:
                print("📊 Changes Detected:")
                print("=" * 50)
            
                for line in upgrade_content:
                    if any(keyword in line for keyword in ['op.add_column', 'op.drop_column', 'op.create_table','op.drop_table', 'op.alter_column', 'op.create_index']):
                        print(f"   🔧 {line.strip()}")
                    elif 'op.' in line:
                        print(f"   📝 {line.strip()}")
            else:
                print("ℹ️  No significant changes detected in models.")
                os.remove(file_path)
                return False
                    
        os.remove(file_path)
        print("\n🗑️  Archivo temporal eliminado")
        return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        print(f"\n🧹 Limpiando archivo temporal... {temp_path}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

def make_migration(description: str="", auto_apply: bool=False):
    print("🔧 Make Alembic Migration")
    print("=" * 50)
    print("🔍 Checking current state...")
    run_shell_command(f"{ALEMBIC_COMMAND} current")
 
    is_model_change = check_model_change()
    if not is_model_change:
        print("✅ No model changes detected. Migration not created.")
        return
    
    revision_message = description if description else "auto_migration"
    
    print(f"📝 Creating new migration with message: '{revision_message}'")
    
    command = f"{ALEMBIC_COMMAND} revision --autogenerate -m '{revision_message}'"
    finished_ok, _ = run_shell_command(command)
    
    if not finished_ok:
        return

    if not auto_apply:
        print("✅ Migration created. Please review the migration script before applying. Use --upgrade to apply.")
        return
    
    apply_migrations()
    return

def apply_migrations(target: str="head"):
    print("🔧 Apply Alembic Migrations")
    print("=" * 50)

    checked_migrations_status = check_pending_migrations()
    if checked_migrations_status in [MigrationAction.PENDING, MigrationAction.NOTMIGRATIONAPPLIED]:
        print(f"🚀 Applying migrations up to: {target}")
        command = f"{ALEMBIC_COMMAND} upgrade {target}"
        finished_ok, _ = run_shell_command(command)
    
        if not finished_ok:
            print("❌ Error applying migrations.")
            return
        print("✅ Migrations applied successfully.")

def main():
    parser = argparse.ArgumentParser(description='Description to create and apply Alembic migrations.')
    parser.add_argument('description', nargs='*', help='Changes description for the migration')
    parser.add_argument('--no-apply', action='store_true', help='No apply the migration after creation')
    parser.add_argument('--check', action='store_true', help='Only check for changes without applying migration')
    parser.add_argument('--upgrade', action='store_true', help='Only to apply migration')
    
    args = parser.parse_args()
    
    description = ' '.join(args.description) if args.description else ""
    auto_apply = not args.no_apply
    check_only = args.check
    upgrade_only = args.upgrade

    if check_only:
        is_model_change = check_model_change()
        if not is_model_change:
            print("✅ No model changes detected.")
            return
        check_migrations_status = check_pending_migrations()
        if check_migrations_status == MigrationAction.ERROR:
            return
        return
    if upgrade_only:
        apply_migrations()
        return
    
    make_migration(description, auto_apply)
        
if __name__ == "__main__":
    main()
