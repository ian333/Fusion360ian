"""
HDriveSimple.py - Versión SIMPLE del Harmonic Drive Generator
Usa nuestra biblioteca wrapper para crear los componentes de forma más fácil
"""

import adsk.core
import adsk.fusion
import traceback
import math
import sys
import os

# Agregar la carpeta actual al path
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importar nuestra biblioteca
from fusion_lib import FusionWrapper, SimpleGear

# Variables globales
app = None
ui = None
handlers = []

def run(context):
    """Punto de entrada principal"""
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Crear comando
        cmd_defs = ui.commandDefinitions
        
        # Eliminar comando anterior si existe
        cmd_def = cmd_defs.itemById('HDriveSimpleCmd')
        if cmd_def:
            cmd_def.deleteMe()
        
        # Crear nuevo comando
        cmd_def = cmd_defs.addButtonDefinition(
            'HDriveSimpleCmd',
            '🔧 Harmonic Drive Simple',
            'Genera un Harmonic Drive usando biblioteca simplificada'
        )
        
        # Agregar manejador
        on_command_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)
        
        # Agregar botón al panel
        panels = ui.allToolbarPanels
        panel = panels.itemById('SolidScriptsAddinsPanel')
        button = panel.controls.addCommand(cmd_def)
        button.isPromoted = True
        
        ui.messageBox('🔧 Harmonic Drive Simple cargado!\n\nVersión simplificada con biblioteca wrapper')
        
    except:
        if ui:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Limpieza"""
    try:
        panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        button = panel.controls.itemById('HDriveSimpleCmd')
        if button:
            button.deleteMe()
        
        cmd_def = ui.commandDefinitions.itemById('HDriveSimpleCmd')
        if cmd_def:
            cmd_def.deleteMe()
    except:
        pass

class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            
            # Título
            inputs.addTextBoxCommandInput('title', '', 
                '<b>🔧 Harmonic Drive Generator Simple</b><br>' +
                '<i>Versión simplificada con biblioteca wrapper</i>', 
                2, True)
            
            # Parámetros básicos
            module_input = inputs.addFloatSpinnerCommandInput(
                'module', 'Módulo (mm)', 'mm', 
                0.5, 2.0, 0.1, 1.0
            )
            module_input.tooltip = 'Tamaño del diente'
            
            teeth_input = inputs.addIntegerSpinnerCommandInput(
                'teeth_cs', 'Dientes (Circular Spline)', 
                60, 160, 2, 100
            )
            teeth_input.tooltip = 'Número de dientes (debe ser par)'
            
            thickness_input = inputs.addFloatSpinnerCommandInput(
                'thickness', 'Espesor (mm)', 'mm',
                5.0, 50.0, 5.0, 20.0
            )
            
            # Info calculada
            inputs.addTextBoxCommandInput('info', '', 
                '<b>Información:</b><br>' +
                'Dientes Flex Spline: 98<br>' +
                'Reducción: 50:1<br>' +
                'Excentricidad: 0.64mm', 
                3, True)
            
            # Agregar manejadores
            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)
            
            on_input_changed = InputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            handlers.append(on_input_changed)
            
        except:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))

class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.inputs
            changed = args.input
            
            if changed.id in ['module', 'teeth_cs']:
                module = inputs.itemById('module').value
                teeth_cs = int(inputs.itemById('teeth_cs').value)
                teeth_fs = teeth_cs - 2
                ratio = teeth_cs // 2
                eccentricity = (2 * module) / math.pi
                
                info = inputs.itemById('info')
                info.text = (
                    f'<b>Información:</b><br>'
                    f'Dientes Flex Spline: {teeth_fs}<br>'
                    f'Reducción: {ratio}:1<br>'
                    f'Excentricidad: {eccentricity:.2f}mm'
                )
        except:
            pass

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            
            # Obtener parámetros
            module_mm = inputs.itemById('module').value
            teeth_cs = int(inputs.itemById('teeth_cs').value)
            thickness_mm = inputs.itemById('thickness').value
            
            # Crear el Harmonic Drive
            create_harmonic_drive_simple(module_mm, teeth_cs, thickness_mm)
            
            ui.messageBox(
                f'✅ Harmonic Drive creado!\n\n'
                f'Módulo: {module_mm}mm\n'
                f'Dientes CS: {teeth_cs}\n'
                f'Dientes FS: {teeth_cs-2}\n'
                f'Reducción: {teeth_cs//2}:1'
            )
            
        except Exception as e:
            ui.messageBox(f'Error: {str(e)}\n\n{traceback.format_exc()}')

def create_harmonic_drive_simple(module_mm, teeth_cs, thickness_mm):
    """
    Crea un Harmonic Drive usando la biblioteca simplificada
    """
    
    # Inicializar wrapper y generador
    fusion = FusionWrapper()
    gear_gen = SimpleGear()
    
    # Calcular parámetros
    teeth_fs = teeth_cs - 2
    pitch_dia_cs_mm = module_mm * teeth_cs
    pitch_dia_fs_mm = module_mm * teeth_fs
    eccentricity_mm = (2 * module_mm) / math.pi
    
    # ========== CIRCULAR SPLINE (Engranaje externo con dientes internos) ==========
    print("Creando Circular Spline...")
    cs_component = gear_gen.crear_engranaje_interno(
        num_dientes=teeth_cs,
        modulo_mm=module_mm,
        espesor_mm=thickness_mm,
        ancho_anillo_mm=10.0,
        nombre="CircularSpline"
    )
    
    # ========== FLEX SPLINE (Copa flexible con dientes externos) ==========
    print("Creando Flex Spline...")
    
    # Crear componente para Flex Spline
    fs_component = fusion.crear_componente(f"FlexSpline_{teeth_fs}T")
    
    # Crear sketch para la copa
    sketch_fs = fusion.crear_sketch(fs_component, "XY")
    
    # Dibujar anillo de la copa (pared delgada)
    radio_exterior_mm = pitch_dia_fs_mm / 2
    grosor_pared_mm = module_mm * 1.5  # Pared delgada para flexibilidad
    radio_interior_mm = radio_exterior_mm - grosor_pared_mm
    
    # Convertir a cm
    radio_ext_cm = fusion.mm_a_cm(radio_exterior_mm)
    radio_int_cm = fusion.mm_a_cm(radio_interior_mm)
    
    # Dibujar círculos
    fusion.dibujar_circulo(sketch_fs, 0, 0, radio_ext_cm)
    fusion.dibujar_circulo(sketch_fs, 0, 0, radio_int_cm)
    
    # Extruir copa (más alta que el CS)
    altura_copa_cm = fusion.mm_a_cm(thickness_mm * 2)  # Copa más alta
    perfil_copa = sketch_fs.profiles.item(0)
    extrusion_copa = fusion.extruir(perfil_copa, altura_copa_cm, fs_component, "nuevo")
    
    # Agregar fondo a la copa
    sketch_fondo = fusion.crear_sketch(fs_component, "XY")
    fusion.dibujar_circulo(sketch_fondo, 0, 0, radio_int_cm)
    perfil_fondo = sketch_fondo.profiles.item(0)
    fusion.extruir(perfil_fondo, fusion.mm_a_cm(3), fs_component, "unir")
    
    # Aplicar color verde (flexible)
    if extrusion_copa.bodies.count > 0:
        fusion.aplicar_color(extrusion_copa.bodies.item(0), "Flex_Green", 100, 200, 100)
    
    # ========== WAVE GENERATOR (Leva elíptica) ==========
    print("Creando Wave Generator...")
    
    # Crear componente
    wg_component = fusion.crear_componente(f"WaveGenerator")
    
    # Crear sketch para la elipse
    sketch_wg = fusion.crear_sketch(wg_component, "XY")
    
    # Calcular dimensiones de la elipse
    radio_base_mm = radio_interior_mm - 2  # Un poco más pequeño que el FS
    ecc_cm = fusion.mm_a_cm(eccentricity_mm)
    radio_base_cm = fusion.mm_a_cm(radio_base_mm)
    
    # Dibujar elipse usando puntos
    # (Fusion no tiene elipse directa, así que usamos spline)
    points = adsk.core.ObjectCollection.create()
    num_points = 60
    
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        # Elipse: radio mayor = base + ecc, radio menor = base - ecc/2
        x = (radio_base_cm + ecc_cm) * math.cos(angle)
        y = (radio_base_cm - ecc_cm * 0.5) * math.sin(angle)
        points.add(fusion.crear_punto(x, y, 0))
    
    # Cerrar la curva
    points.add(points.item(0))
    
    # Crear spline
    curves = sketch_wg.sketchCurves
    spline = curves.sketchFittedSplines.add(points)
    
    # Agregar agujero central para eje
    fusion.dibujar_circulo(sketch_wg, 0, 0, fusion.mm_a_cm(5))  # Agujero de 10mm
    
    # Extruir Wave Generator
    perfiles = sketch_wg.profiles
    for i in range(perfiles.count):
        perfil = perfiles.item(i)
        if perfil.profileLoops.count == 2:  # Perfil con agujero
            extrusion_wg = fusion.extruir(
                perfil, 
                fusion.mm_a_cm(thickness_mm * 0.8),  # Un poco menos alto
                wg_component, 
                "nuevo"
            )
            
            # Aplicar color rojo
            if extrusion_wg.bodies.count > 0:
                fusion.aplicar_color(extrusion_wg.bodies.item(0), "WG_Red", 200, 100, 100)
            break
    
    # Mover componentes para visualización
    # El Flex Spline un poco arriba
    transform = adsk.core.Matrix3D.create()
    transform.translation = adsk.core.Vector3D.create(0, 0, fusion.mm_a_cm(2))
    fs_component.transform = transform
    
    # El Wave Generator más arriba
    transform2 = adsk.core.Matrix3D.create()
    transform2.translation = adsk.core.Vector3D.create(0, 0, fusion.mm_a_cm(5))
    wg_component.transform = transform2
    
    print("✅ Harmonic Drive creado exitosamente!")
    
    return True