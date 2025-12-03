#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Añadir el directorio raíz al path para imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from app.infrastructure.settings.api_settings import settings

def run_command(command, cwd=None):
    """Ejecuta un comando y muestra el output"""
    print(f"➡️  Ejecutando: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ Error: {result.stderr}")
        return False
    if result.stdout:
        print(f"✅ Output: {result.stdout}")
    return True

def confirm_action(message):
    """Pedir confirmación antes de una acción destructiva"""
    print(f"\n⚠️  {message}")
    response = input("¿Estás seguro? (sí/NO): ").lower().strip()
    return response in ['sí', 'si', 's', 'yes', 'y']

def clean_migration_files():
    """Eliminar archivos de migración"""
    print("\n📄 Limpiando archivos de migración...")
    
    versions_dir = "app/infrastructure/migration/alembic/versions"
    
    if os.path.exists(versions_dir):
        # Contar archivos a eliminar
        migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and f != '__init__.py']
        
        if migration_files:
            print(f"📊 Encontrados {len(migration_files)} archivos de migración:")
            for file in migration_files:
                print(f"   - {file}")
            
            if confirm_action(f"¿Eliminar {len(migration_files)} archivos de migración?"):
                for file in migration_files:
                    file_path = os.path.join(versions_dir, file)
                    os.remove(file_path)
                    print(f"✅ Eliminado: {file}")
            else:
                print("⏭️  Saltando eliminación de archivos de migración")
        else:
            print("ℹ️  No hay archivos de migración para eliminar")
    else:
        print("ℹ️  El directorio de versions no existe")
    
    return True

def clean_alembic_version_table():
    """Limpiar la tabla de versiones de Alembic en la base de datos"""
    print("\n🗄️  Limpiando tabla de versiones de Alembic...")
    
    # Esto elimina la tabla alembic_version si existe
    cleanup_sql = """
    DO $$ 
    BEGIN 
        DROP TABLE IF EXISTS alembic_version CASCADE;
    EXCEPTION 
        WHEN others THEN 
            -- Ignorar errores si la tabla no existe
            NULL;
    END $$;
    """
    
    try:
        # Guardar SQL en un archivo temporal
        temp_file = "temp_cleanup.sql"
        with open(temp_file, 'w') as f:
            f.write(cleanup_sql)
        
        # Ejecutar con psql
        cmd = f'psql {settings.database_url} -f {temp_file}'
        if run_command(cmd):
            print("✅ Tabla alembic_version eliminada")
        
        # Limpiar archivo temporal
        os.remove(temp_file)
        return True
        
    except Exception as e:
        print(f"⚠️  No se pudo limpiar la tabla alembic_version: {e}")
        return True  # Continuar aunque falle

def clean_pycache_directories():
    """Limpiar directorios __pycache__"""
    print("\n🧹 Limpiando archivos cache de Python...")
    
    cache_dirs = []
    for root, dirs, files in os.walk("app/infrastructure/migration"):
        if '__pycache__' in dirs:
            cache_dirs.append(os.path.join(root, '__pycache__'))
    
    for cache_dir in cache_dirs:
        try:
            shutil.rmtree(cache_dir)
            print(f"✅ Eliminado: {cache_dir}")
        except Exception as e:
            print(f"⚠️  Error eliminando {cache_dir}: {e}")
    
    return True

def reset_alembic_history():
    """Resetear el historial de Alembic"""
    print("\n🔄 Reseteando historial de Alembic...")
    
    # Eliminar el directorio alembic y recrearlo
    alembic_dir = "app/infrastructure/migration/alembic"
    
    if os.path.exists(alembic_dir):
        if confirm_action("¿Eliminar y recrear la configuración completa de Alembic?"):
            shutil.rmtree(alembic_dir)
            print("✅ Directorio alembic eliminado")
            
            # Recrear Alembic
            if run_command("alembic init app/infrastructure/migration/alembic"):
                print("✅ Alembic reinicializado")
        else:
            print("⏭️  Saltando reset completo de Alembic")
    else:
        print("ℹ️  El directorio alembic no existe")
    
    return True

def show_current_state():
    """Mostrar el estado actual"""
    print("\n📊 ESTADO ACTUAL:")
    
    # Verificar directorios
    versions_dir = "app/infrastructure/migration/alembic/versions"
    if os.path.exists(versions_dir):
        migration_files = [f for f in os.listdir(versions_dir) if f.endswith('.py') and f != '__init__.py']
        print(f"   Archivos de migración: {len(migration_files)}")
        for file in migration_files[:5]:  # Mostrar solo los primeros 5
            print(f"     - {file}")
        if len(migration_files) > 5:
            print(f"     ... y {len(migration_files) - 5} más")
    else:
        print("   Directorio de versions: No existe")
    
    # Verificar contenedores Docker
    result = subprocess.run("docker ps -f name=postgres_db --format '{{.Names}}'", 
                          shell=True, capture_output=True, text=True)
    if "postgres_db" in result.stdout:
        print("   Contenedor PostgreSQL: En ejecución")
    else:
        print("   Contenedor PostgreSQL: Detenido")

def main():
    print("🚨 LIMPIADOR COMPLETO DE MIGRACIONES")
    print("=" * 50)
    print("⚠️  ADVERTENCIA: Esta operación es destructiva")
    print("⚠️  Solo para entornos de desarrollo")
    print("=" * 50)
    
    # Mostrar estado actual
    show_current_state()
    
    if not confirm_action("¿Quieres proceder con la limpieza completa?"):
        print("❌ Operación cancelada")
        return
    
    steps = [
        ("Limpiar archivos de migración", clean_migration_files),
        ("Limpiar tabla de versiones", clean_alembic_version_table),
        ("Limpiar cache de Python", clean_pycache_directories),
        ("Resetear historial Alembic", reset_alembic_history),
    ]
    
    all_success = True
    for step_name, step_function in steps:
        print(f"\n{'='*40}")
        print(f"PASO: {step_name}")
        print(f"{'='*40}")
        if not step_function():
            all_success = False
            print(f"❌ Error en: {step_name}")
            if not confirm_action("¿Continuar con los siguientes pasos?"):
                break
    
    if all_success:
        print("\n🎉 ¡Limpieza completada exitosamente!")
        print("\n📝 Próximos pasos:")
        print("   1. Ejecuta: python app/infrastructure/migration/setup_migration_system.py")
        print("   2. O ejecuta: python app/infrastructure/migration/init_migration.py")
    else:
        print("\n⚠️  La limpieza tuvo algunos errores")
        print("   Revisa los mensajes arriba")

if __name__ == "__main__":
    main()
