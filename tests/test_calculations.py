# -*- coding: utf-8 -*-
"""
test_calculations.py - Tests para los cálculos del Harmonic Drive
Se puede ejecutar independientemente sin Fusion 360
"""

import sys
import os
import math

# Agregar el directorio padre al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.calculations import (
    HarmonicDriveParams, 
    HarmonicDriveCalculator,
    quick_validation,
    suggest_parameters
)


def test_basic_parameters():
    """Test de parámetros básicos"""
    print("\n" + "="*60)
    print("TEST 1: Parámetros Básicos")
    print("="*60)
    
    # Crear parámetros para 100:1 de reducción
    params = HarmonicDriveParams(
        teeth_cs=200,
        module=0.5,
        pressure_angle=30
    )
    
    print(f"Entrada:")
    print(f"  Dientes CS: {params.teeth_cs}")
    print(f"  Módulo: {params.module} mm")
    print(f"  Ángulo presión: {params.pressure_angle}°")
    
    print(f"\nCalculados:")
    print(f"  Dientes FS: {params.teeth_fs}")
    print(f"  Relación reducción: {params.ratio}:1")
    print(f"  Excentricidad: {params.eccentricity:.3f} mm")
    
    # Verificaciones
    assert params.teeth_fs == 198, "Error: FS debe tener 2 dientes menos"
    assert params.ratio == 100, "Error: Relación debe ser 100:1"
    assert abs(params.eccentricity - 0.318) < 0.001, "Error: Excentricidad incorrecta"
    
    print("\n✅ Test 1 PASADO")
    return True


def test_circular_spline_geometry():
    """Test de geometría del Circular Spline"""
    print("\n" + "="*60)
    print("TEST 2: Geometría Circular Spline")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    cs_geo = calc.get_circular_spline_geometry()
    
    print(f"Circular Spline (engranaje interno):")
    print(f"  Tipo: {cs_geo['type']}")
    print(f"  Dientes: {cs_geo['teeth']}")
    print(f"  Diámetro primitivo: {cs_geo['pitch_diameter']:.2f} mm")
    print(f"  Diámetro addendum: {cs_geo['addendum_diameter']:.2f} mm (interior)")
    print(f"  Diámetro dedendum: {cs_geo['dedendum_diameter']:.2f} mm (exterior)")
    print(f"  Diámetro base: {cs_geo['base_diameter']:.2f} mm")
    print(f"  Diámetro exterior: {cs_geo['outer_diameter']:.2f} mm")
    
    # Verificaciones
    assert cs_geo['type'] == 'internal', "Debe ser engranaje interno"
    assert cs_geo['pitch_diameter'] == 100, "Diámetro primitivo = módulo × dientes"
    assert cs_geo['addendum_diameter'] < cs_geo['pitch_diameter'], "Addendum debe ser menor en interno"
    assert cs_geo['dedendum_diameter'] > cs_geo['pitch_diameter'], "Dedendum debe ser mayor en interno"
    
    print("\n✅ Test 2 PASADO")
    return True


def test_flex_spline_geometry():
    """Test de geometría del Flex Spline"""
    print("\n" + "="*60)
    print("TEST 3: Geometría Flex Spline")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    fs_geo = calc.get_flex_spline_geometry()
    
    print(f"Flex Spline (engranaje externo flexible):")
    print(f"  Tipo: {fs_geo['type']}")
    print(f"  Dientes: {fs_geo['teeth']}")
    print(f"  Diámetro primitivo: {fs_geo['pitch_diameter']:.2f} mm")
    print(f"  Diámetro addendum: {fs_geo['addendum_diameter']:.2f} mm (exterior)")
    print(f"  Diámetro dedendum: {fs_geo['dedendum_diameter']:.2f} mm (interior)")
    print(f"  Diámetro interior copa: {fs_geo['inner_diameter']:.2f} mm")
    print(f"  Espesor pared: {fs_geo['wall_thickness']:.2f} mm")
    print(f"  Longitud copa: {fs_geo['cup_length']:.2f} mm")
    
    # Verificaciones
    assert fs_geo['type'] == 'external', "Debe ser engranaje externo"
    assert fs_geo['teeth'] == 98, "Debe tener 2 dientes menos que CS"
    assert fs_geo['addendum_diameter'] > fs_geo['pitch_diameter'], "Addendum debe ser mayor en externo"
    assert fs_geo['dedendum_diameter'] < fs_geo['pitch_diameter'], "Dedendum debe ser menor en externo"
    
    print("\n✅ Test 3 PASADO")
    return True


def test_wave_generator_geometry():
    """Test de geometría del Wave Generator"""
    print("\n" + "="*60)
    print("TEST 4: Geometría Wave Generator")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    wg_geo = calc.get_wave_generator_geometry()
    
    print(f"Wave Generator (leva elíptica):")
    print(f"  Tipo: {wg_geo['type']}")
    print(f"  Radio mayor: {wg_geo['major_radius']:.2f} mm")
    print(f"  Radio menor: {wg_geo['minor_radius']:.2f} mm")
    print(f"  Excentricidad: {wg_geo['eccentricity']:.3f} mm")
    print(f"  Diámetro eje: {wg_geo['shaft_diameter']:.2f} mm")
    print(f"  Altura: {wg_geo['height']:.2f} mm")
    
    # Verificaciones
    diff = wg_geo['major_radius'] - wg_geo['minor_radius']
    expected_diff = 2 * params.eccentricity
    assert abs(diff - expected_diff) < 0.01, "Diferencia de radios debe ser 2×excentricidad"
    
    print("\n✅ Test 4 PASADO")
    return True


def test_strain_calculation():
    """Test del cálculo de deformación"""
    print("\n" + "="*60)
    print("TEST 5: Cálculo de Deformación (Strain)")
    print("="*60)
    
    # Test con diferentes materiales
    materials = ['steel', 'aluminum', 'plastic', 'tpu']
    
    for material in materials:
        params = HarmonicDriveParams(
            teeth_cs=100, 
            module=1.0, 
            pressure_angle=30,
            material=material
        )
        calc = HarmonicDriveCalculator(params)
        strain = calc.calculate_strain()
        
        print(f"\nMaterial: {material}")
        print(f"  Deformación: {strain['strain_percent']:.3f}%")
        print(f"  Límite máximo: {strain['max_strain_percent']:.2f}%")
        print(f"  ¿Es seguro?: {'SÍ ✅' if strain['is_safe'] else 'NO ❌'}")
        print(f"  Factor de seguridad: {strain['safety_factor']:.2f}")
    
    print("\n✅ Test 5 PASADO")
    return True


def test_contact_ratio():
    """Test de la relación de contacto"""
    print("\n" + "="*60)
    print("TEST 6: Relación de Contacto")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    contact_ratio = calc.calculate_contact_ratio()
    
    print(f"Relación de contacto: {contact_ratio:.2f}")
    print(f"Mínimo requerido: 1.2")
    print(f"Estado: {'✅ OK' if contact_ratio > 1.2 else '❌ BAJO'}")
    
    assert contact_ratio > 1.0, "Relación de contacto debe ser > 1.0"
    
    print("\n✅ Test 6 PASADO")
    return True


def test_backlash():
    """Test del cálculo de juego (backlash)"""
    print("\n" + "="*60)
    print("TEST 7: Cálculo de Juego (Backlash)")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    backlash = calc.calculate_backlash()
    
    print(f"Juego tangencial:")
    print(f"  Mínimo: {backlash['tangential_min']:.3f} mm")
    print(f"  Máximo: {backlash['tangential_max']:.3f} mm")
    print(f"  Nominal: {backlash['tangential_nominal']:.3f} mm")
    print(f"Juego radial nominal: {backlash['radial_nominal']:.3f} mm")
    
    # Verificación
    assert backlash['tangential_nominal'] == 0.05 * params.module, "Juego debe ser 5% del módulo"
    
    print("\n✅ Test 7 PASADO")
    return True


def test_involute_profile():
    """Test del perfil involuta"""
    print("\n" + "="*60)
    print("TEST 8: Perfil Involuta")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    # Generar puntos del perfil
    points_external = calc.get_involute_profile_points(num_points=10, is_internal=False)
    points_internal = calc.get_involute_profile_points(num_points=10, is_internal=True)
    
    print(f"Perfil externo (FS) - primeros 5 puntos:")
    for i, (x, y) in enumerate(points_external[:5]):
        print(f"  Punto {i}: ({x:.3f}, {y:.3f})")
    
    print(f"\nPerfil interno (CS) - primeros 5 puntos:")
    for i, (x, y) in enumerate(points_internal[:5]):
        print(f"  Punto {i}: ({x:.3f}, {y:.3f})")
    
    # Verificar que se generaron puntos
    assert len(points_external) == 10, "Debe generar 10 puntos"
    assert len(points_internal) == 10, "Debe generar 10 puntos"
    
    print("\n✅ Test 8 PASADO")
    return True


def test_quick_validation():
    """Test de validación rápida"""
    print("\n" + "="*60)
    print("TEST 9: Validación Rápida")
    print("="*60)
    
    # Casos de prueba
    test_cases = [
        (100, 1.0, 'steel', True, "Configuración estándar"),
        (50, 1.0, 'steel', False, "Muy pocos dientes"),
        (100, 0.1, 'steel', False, "Módulo muy pequeño"),
        (100, 0.5, 'plastic', True, "Plástico OK"),
        (200, 0.3, 'steel', True, "Alta reducción"),
    ]
    
    for teeth, module, material, should_pass, description in test_cases:
        is_valid, messages = quick_validation(teeth, module, material)
        
        print(f"\n{description}:")
        print(f"  Dientes: {teeth}, Módulo: {module}, Material: {material}")
        print(f"  Resultado: {'✅ VÁLIDO' if is_valid else '❌ INVÁLIDO'}")
        
        if messages:
            print("  Mensajes:")
            for msg in messages:
                print(f"    - {msg}")
        
        if should_pass:
            assert is_valid, f"Debería pasar: {description}"
        else:
            assert not is_valid, f"Debería fallar: {description}"
    
    print("\n✅ Test 9 PASADO")
    return True


def test_parameter_suggestion():
    """Test de sugerencia de parámetros"""
    print("\n" + "="*60)
    print("TEST 10: Sugerencia de Parámetros")
    print("="*60)
    
    # Solicitar parámetros para diferentes reducciones
    test_ratios = [50, 80, 100, 160]
    
    for ratio in test_ratios:
        params = suggest_parameters(
            reduction_ratio=ratio,
            max_diameter=150,
            material='steel'
        )
        
        if params:
            print(f"\nReducción {ratio}:1")
            print(f"  Dientes CS: {params.teeth_cs}")
            print(f"  Dientes FS: {params.teeth_fs}")
            print(f"  Módulo: {params.module} mm")
            print(f"  Diámetro: {params.module * params.teeth_cs:.1f} mm")
            
            # Verificar
            calc = HarmonicDriveCalculator(params)
            strain = calc.calculate_strain()
            print(f"  Deformación: {strain['strain_percent']:.3f}%")
            print(f"  Seguro: {'✅' if strain['is_safe'] else '❌'}")
        else:
            print(f"\nNo se puede lograr {ratio}:1 con los límites dados")
    
    print("\n✅ Test 10 PASADO")
    return True


def test_full_summary():
    """Test del resumen completo"""
    print("\n" + "="*60)
    print("TEST 11: Resumen Completo")
    print("="*60)
    
    params = HarmonicDriveParams(teeth_cs=100, module=1.0, pressure_angle=30)
    calc = HarmonicDriveCalculator(params)
    
    summary = calc.get_full_summary()
    
    print("\nRESUMEN DEL HARMONIC DRIVE:")
    print("-" * 40)
    
    print("\nParámetros principales:")
    for key, value in summary['parameters'].items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    print("\nAnálisis:")
    print(f"  Deformación: {summary['analysis']['strain']['strain_percent']:.3f}%")
    print(f"  Relación contacto: {summary['analysis']['contact_ratio']:.2f}")
    print(f"  Juego nominal: {summary['analysis']['backlash']['tangential_nominal']:.3f} mm")
    print(f"  ¿DISEÑO VÁLIDO?: {'✅ SÍ' if summary['analysis']['is_valid'] else '❌ NO'}")
    
    assert 'parameters' in summary
    assert 'circular_spline' in summary
    assert 'flex_spline' in summary
    assert 'wave_generator' in summary
    assert 'analysis' in summary
    
    print("\n✅ Test 11 PASADO")
    return True


def run_all_tests():
    """Ejecuta todos los tests"""
    print("\n" + "="*60)
    print("EJECUTANDO SUITE COMPLETA DE TESTS")
    print("="*60)
    
    tests = [
        ("Parámetros Básicos", test_basic_parameters),
        ("Geometría CS", test_circular_spline_geometry),
        ("Geometría FS", test_flex_spline_geometry),
        ("Geometría WG", test_wave_generator_geometry),
        ("Cálculo Strain", test_strain_calculation),
        ("Relación Contacto", test_contact_ratio),
        ("Backlash", test_backlash),
        ("Perfil Involuta", test_involute_profile),
        ("Validación Rápida", test_quick_validation),
        ("Sugerencia Parámetros", test_parameter_suggestion),
        ("Resumen Completo", test_full_summary)
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"\n❌ ERROR en {name}: {str(e)}")
            failed += 1
    
    print("\n" + "="*60)
    print("RESUMEN DE TESTS")
    print("="*60)
    print(f"✅ Pasados: {passed}")
    print(f"❌ Fallados: {failed}")
    print(f"📊 Total: {passed + failed}")
    
    if failed == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON!")
    else:
        print(f"\n⚠️ {failed} tests fallaron")
    
    return failed == 0


if __name__ == "__main__":
    # Ejecutar todos los tests cuando se llame directamente
    success = run_all_tests()
    
    # Ejemplo de uso interactivo
    if success:
        print("\n" + "="*60)
        print("EJEMPLO DE USO INTERACTIVO")
        print("="*60)
        
        print("\nCreando un Harmonic Drive 80:1...")
        params = suggest_parameters(reduction_ratio=80, max_diameter=100)
        
        if params:
            calc = HarmonicDriveCalculator(params)
            summary = calc.get_full_summary()
            
            print(f"\nDiseño óptimo encontrado:")
            print(f"  Módulo: {params.module} mm")
            print(f"  Dientes: {params.teeth_cs} (CS) / {params.teeth_fs} (FS)")
            print(f"  Diámetro: {params.module * params.teeth_cs:.1f} mm")
            print(f"  Válido: {'✅' if summary['analysis']['is_valid'] else '❌'}")