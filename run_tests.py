#!/usr/bin/env python
"""
Script para ejecutar tests automatizados del proyecto
"""
import os
import sys
import subprocess

def run_command(command, description):
    """Ejecuta un comando y muestra el resultado"""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} - EXITOSO")
        if result.stdout:
            print(result.stdout)
    else:
        print(f"❌ {description} - FALLÓ")
        if result.stderr:
            print(result.stderr)
        if result.stdout:
            print(result.stdout)
    
    return result.returncode == 0

def main():
    """Función principal"""
    print("🚀 EJECUTANDO TESTS AUTOMATIZADOS")
    print("=" * 50)
    
    # Configurar entorno Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    
    tests_passed = 0
    total_tests = 0
    
    # Lista de tests a ejecutar
    test_commands = [
        ("pytest test_stock_ventas.py -v", "Tests de Stock y Ventas"),
        ("pytest test_auth_permisos.py -v", "Tests de Autenticación y Permisos"),
        ("pytest --cov=stock_ventas --cov=club --cov-report=term-missing", "Coverage Report"),
    ]
    
    for command, description in test_commands:
        total_tests += 1
        if run_command(command, description):
            tests_passed += 1
    
    # Resumen final
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN: {tests_passed}/{total_tests} tests exitosos")
    
    if tests_passed == total_tests:
        print("🎉 ¡TODOS LOS TESTS PASARON!")
        return 0
    else:
        print("⚠️  Algunos tests fallaron. Revisar errores arriba.")
        return 1

if __name__ == "__main__":
    sys.exit(main())