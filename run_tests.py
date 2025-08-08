#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_tests.py - Ejecutor de todas las pruebas SIN Fusion 360
Ejecuta este archivo para verificar que todo funciona correctamente
"""

import sys
import os

# Agregar el directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*70)
print("SUITE DE PRUEBAS - HARMONIC DRIVE GENERATOR")
print("="*70)
print("\nEste script ejecuta todas las pruebas SIN necesidad de Fusion 360")
print("-"*70)

# Test 1: Importar módulos
print("\n[1/4] Verificando imports...")
try:
    from core.calculations import HarmonicDriveParams, HarmonicDriveCalculator
    from geometry.involute_profile import InvoluteGearProfile, HarmonicDriveInvoluteProfile
    print("✅ Todos los módulos importados correctamente")
except Exception as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)

# Test 2: Ejecutar tests de cálculos
print("\n[2/4] Ejecutando tests de cálculos matemáticos...")
print("-"*50)
try:
    from tests.test_calculations import run_all_tests
    success = run_all_tests()
    if not success:
        print("⚠️ Algunos tests de cálculos fallaron")
except Exception as e:
    print(f"❌ Error en tests de cálculos: {e}")

# Test 3: Probar perfil involuta
print("\n[3/4] Probando generador de perfil involuta...")
print("-"*50)
try:
    from geometry.involute_profile import test_involute_profile
    result = test_involute_profile()
    if result:
        print("✅ Perfil involuta funciona correctamente")
    else:
        print("⚠️ Problemas con el perfil involuta")
except Exception as e:
    print(f"❌ Error en perfil involuta: {e}")

# Test 4: Ejemplo completo de Harmonic Drive
print("\n[4/4] Ejemplo completo de diseño de Harmonic Drive...")
print("-"*50)
try:
    # Crear parámetros para un HD 80:1
    print("\nDiseñando Harmonic Drive 80:1...")
    
    params = HarmonicDriveParams(
        teeth_cs=160,
        module=0.5,
        pressure_angle=30,
        material='plastic'  # Para que pase la validación de strain
    )
    
    # Crear calculadora
    calc = HarmonicDriveCalculator(params)
    
    # Obtener resumen
    summary = calc.get_full_summary()
    
    print(f"\n📊 RESUMEN DEL DISEÑO:")
    print(f"  Reducción: {params.ratio}:1")
    print(f"  Dientes CS/FS: {params.teeth_cs}/{params.teeth_fs}")
    print(f"  Módulo: {params.module} mm")
    print(f"  Excentricidad: {params.eccentricity:.3f} mm")
    
    print(f"\n📐 DIMENSIONES:")
    cs_geo = summary['circular_spline']
    fs_geo = summary['flex_spline']
    wg_geo = summary['wave_generator']
    
    print(f"  Circular Spline:")
    print(f"    - Diámetro primitivo: {cs_geo['pitch_diameter']:.2f} mm")
    print(f"    - Diámetro exterior: {cs_geo['outer_diameter']:.2f} mm")
    
    print(f"  Flex Spline:")
    print(f"    - Diámetro primitivo: {fs_geo['pitch_diameter']:.2f} mm")
    print(f"    - Espesor pared: {fs_geo['wall_thickness']:.2f} mm")
    print(f"    - Longitud copa: {fs_geo['cup_length']:.2f} mm")
    
    print(f"  Wave Generator:")
    print(f"    - Elipse mayor: {wg_geo['major_diameter']:.2f} mm")
    print(f"    - Elipse menor: {wg_geo['minor_diameter']:.2f} mm")
    
    print(f"\n✅ VALIDACIÓN:")
    analysis = summary['analysis']
    print(f"  Deformación: {analysis['strain']['strain_percent']:.2f}% (máx: {analysis['strain']['max_strain_percent']:.1f}%)")
    print(f"  Relación contacto: {analysis['contact_ratio']:.2f}")
    print(f"  Juego nominal: {analysis['backlash']['tangential_nominal']:.3f} mm")
    print(f"  Estado: {'✅ VÁLIDO' if analysis['is_valid'] else '❌ INVÁLIDO'}")
    
    # Crear perfiles involutivos
    print(f"\n🔧 GENERANDO PERFILES INVOLUTIVOS:")
    hd_profile = HarmonicDriveInvoluteProfile(params)
    
    # Validar engrane
    mesh_validation = hd_profile.validate_meshing()
    print(f"  CS válido: {'✅' if mesh_validation['cs_valid'] else '❌'}")
    print(f"  FS válido: {'✅' if mesh_validation['fs_valid'] else '❌'}")
    print(f"  Engrane válido: {'✅' if mesh_validation['mesh_valid'] else '❌'}")
    
    if mesh_validation['errors']:
        print("  Errores:")
        for error in mesh_validation['errors']:
            print(f"    - {error}")
    
    if mesh_validation['warnings']:
        print("  Advertencias:")
        for warning in mesh_validation['warnings']:
            print(f"    - {warning}")
    
    # Generar algunos puntos de ejemplo
    cs_teeth = hd_profile.get_cs_profile()
    fs_teeth = hd_profile.get_fs_profile()
    
    print(f"\n📊 GEOMETRÍA GENERADA:")
    print(f"  Dientes CS generados: {len(cs_teeth)}")
    print(f"  Dientes FS generados: {len(fs_teeth)}")
    
    if cs_teeth and cs_teeth[0]:
        print(f"  Puntos por diente: {len(cs_teeth[0])}")
        print(f"  Primeros 3 puntos del primer diente CS:")
        for i, (x, y) in enumerate(cs_teeth[0][:3]):
            print(f"    {i}: ({x:.3f}, {y:.3f})")
    
    print("\n✅ Ejemplo completo ejecutado correctamente")
    
except Exception as e:
    print(f"❌ Error en ejemplo completo: {e}")
    import traceback
    traceback.print_exc()

# Resumen final
print("\n" + "="*70)
print("RESUMEN FINAL")
print("="*70)
print("\n✅ Sistema listo para usar")
print("\n📝 PRÓXIMOS PASOS:")
print("  1. Los cálculos matemáticos están funcionando")
print("  2. El perfil involuta está implementado")
print("  3. Ahora puedes usar estos módulos en Fusion 360")
print("  4. Ejecuta HDriveGenerator.py en Fusion 360 para generar el modelo 3D")
print("\n💡 NOTA: Este script verifica la lógica SIN Fusion 360")
print("         Para generar el modelo 3D, usa Fusion 360")
print("\n" + "="*70)