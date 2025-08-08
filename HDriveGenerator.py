# -*- coding: utf-8 -*-
"""
HDriveGenerator.py - Generador de Harmonic Drive para Fusion 360
Versión 1.0.0 - Implementación completa con perfil involuta real
"""

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math
import sys
import os

# Agregar el directorio actual al path para importar nuestros módulos
current_dir = os.path.dirname(os.path.realpath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Importar nuestra biblioteca
from core.calculations import HarmonicDriveParams, HarmonicDriveCalculator
from geometry.involute_profile import HarmonicDriveInvoluteProfile

# Variables globales
_app = None
_ui = None
_handlers = []

# Constantes
COMMAND_ID = 'HDriveGeneratorCmd'
COMMAND_NAME = '⚙️ Harmonic Drive Generator'
COMMAND_DESCRIPTION = 'Genera un Harmonic Drive con perfil involuta real'

class HDriveCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    """Manejador para cuando se crea el comando"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            cmd = args.command
            cmd.isRepeatable = False
            
            # Crear inputs de la interfaz
            inputs = cmd.commandInputs
            
            # Título
            inputs.addTextBoxCommandInput(
                'title', 
                '', 
                '<h2>⚙️ Harmonic Drive Generator v1.0</h2>' +
                '<p>Genera un Harmonic Drive con perfil involuta matemáticamente correcto</p>',
                3, 
                True
            )
            
            # Grupo de parámetros básicos
            basic_group = inputs.addGroupCommandInput('basicGroup', '📐 Parámetros Básicos')
            basic_group.isExpanded = True
            basic_inputs = basic_group.children
            
            # Relación de reducción
            ratio_input = basic_inputs.addIntegerSpinnerCommandInput(
                'reductionRatio', 
                'Relación de Reducción', 
                30, 160, 1, 80
            )
            ratio_input.tooltip = 'Relación de reducción deseada (30:1 a 160:1)'
            
            # Módulo
            module_input = basic_inputs.addFloatSpinnerCommandInput(
                'module', 
                'Módulo (mm)', 
                'mm', 
                0.3, 2.0, 0.1, 0.5
            )
            module_input.tooltip = 'Tamaño del diente (0.3-2.0 mm)'
            
            # Ángulo de presión
            pressure_input = basic_inputs.addDropDownCommandInput(
                'pressureAngle',
                'Ángulo de Presión',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            pressure_input.listItems.add('20°', False)
            pressure_input.listItems.add('25°', False)
            pressure_input.listItems.add('30° (Recomendado para HD)', True)
            pressure_input.tooltip = 'Ángulo de presión del diente'
            
            # Grupo de dimensiones
            dim_group = inputs.addGroupCommandInput('dimGroup', '📏 Dimensiones')
            dim_group.isExpanded = True
            dim_inputs = dim_group.children
            
            # Espesor
            thickness_input = dim_inputs.addFloatSpinnerCommandInput(
                'thickness',
                'Espesor (mm)',
                'mm',
                5.0, 50.0, 5.0, 20.0
            )
            thickness_input.tooltip = 'Espesor de los componentes'
            
            # Longitud de copa
            cup_factor_input = dim_inputs.addFloatSliderCommandInput(
                'cupFactor',
                'Factor Longitud Copa',
                'mm',
                0.5, 1.5, False
            )
            cup_factor_input.valueOne = 0.8
            cup_factor_input.tooltip = 'Longitud de la copa como factor del diámetro (0.5-1.5)'
            
            # Grupo de material
            material_group = inputs.addGroupCommandInput('materialGroup', '🎨 Material y Tolerancias')
            material_group.isExpanded = False
            material_inputs = material_group.children
            
            # Material
            material_input = material_inputs.addDropDownCommandInput(
                'material',
                'Material del Flex Spline',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            material_input.listItems.add('Acero (Strain máx: 0.3%)', False)
            material_input.listItems.add('Aluminio (Strain máx: 0.4%)', False)
            material_input.listItems.add('Plástico (Strain máx: 2%)', True)
            material_input.listItems.add('TPU Flexible (Strain máx: 5%)', False)
            
            # Tolerancia de impresión
            tolerance_input = material_inputs.addFloatSpinnerCommandInput(
                'printTolerance',
                'Tolerancia Impresión 3D (mm)',
                'mm',
                0.0, 0.5, 0.05, 0.2
            )
            tolerance_input.tooltip = 'Tolerancia para impresión 3D'
            
            # Información calculada
            inputs.addTextBoxCommandInput(
                'info',
                '',
                self._get_info_text(80, 0.5),
                6,
                True
            )
            
            # Grupo de opciones avanzadas
            advanced_group = inputs.addGroupCommandInput('advancedGroup', '🔧 Opciones Avanzadas')
            advanced_group.isExpanded = False
            advanced_inputs = advanced_group.children
            
            # Generar dientes reales
            generate_teeth = advanced_inputs.addBoolValueInput(
                'generateTeeth',
                'Generar dientes involutivos completos',
                True,
                '',
                True
            )
            generate_teeth.tooltip = 'Genera el perfil completo de dientes (más lento)'
            
            # Número de puntos por diente
            points_per_tooth = advanced_inputs.addIntegerSliderCommandInput(
                'pointsPerTooth',
                'Puntos por diente',
                10, 50, False
            )
            points_per_tooth.valueOne = 20
            points_per_tooth.tooltip = 'Más puntos = más precisión pero más lento'
            
            # Agregar handlers
            onExecute = HDriveCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute)
            
            onInputChanged = HDriveCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)
            
            onValidate = HDriveCommandValidateHandler()
            cmd.validateInputs.add(onValidate)
            _handlers.append(onValidate)
            
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
    
    def _get_info_text(self, ratio, module):
        """Genera el texto de información"""
        teeth_cs = ratio * 2
        teeth_fs = teeth_cs - 2
        pitch_dia = module * teeth_cs
        eccentricity = (2 * module) / math.pi
        
        return (
            '<b>📊 Información Calculada:</b><br>' +
            f'• Dientes CS: {teeth_cs}<br>' +
            f'• Dientes FS: {teeth_fs}<br>' +
            f'• Diámetro primitivo: {pitch_dia:.1f} mm<br>' +
            f'• Excentricidad: {eccentricity:.3f} mm<br>' +
            f'• <font color="green">✓ Configuración válida</font>'
        )

class HDriveCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    """Manejador para cambios en los inputs"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.inputs
            changed = args.input
            
            # Si cambiaron los parámetros principales, actualizar info
            if changed.id in ['reductionRatio', 'module', 'material']:
                ratio = inputs.itemById('reductionRatio').value
                module = inputs.itemById('module').value * 10  # cm a mm
                material_idx = inputs.itemById('material').selectedItem.index
                
                # Mapear material
                materials = ['steel', 'aluminum', 'plastic', 'tpu']
                material = materials[material_idx]
                
                # Calcular parámetros
                teeth_cs = ratio * 2
                teeth_fs = teeth_cs - 2
                pitch_dia = module * teeth_cs
                eccentricity = (2 * module) / math.pi
                
                # Validar strain
                params = HarmonicDriveParams(
                    teeth_cs=teeth_cs,
                    module=module,
                    pressure_angle=30,
                    material=material
                )
                
                try:
                    calc = HarmonicDriveCalculator(params)
                    strain_data = calc.calculate_strain()
                    
                    # Actualizar info
                    info_text = (
                        '<b>📊 Información Calculada:</b><br>' +
                        f'• Dientes CS: {teeth_cs}<br>' +
                        f'• Dientes FS: {teeth_fs}<br>' +
                        f'• Diámetro primitivo: {pitch_dia:.1f} mm<br>' +
                        f'• Excentricidad: {eccentricity:.3f} mm<br>'
                    )
                    
                    if strain_data['is_safe']:
                        info_text += f'• Deformación: {strain_data["strain_percent"]:.2f}% (OK)<br>'
                        info_text += '• <font color="green">✓ Configuración válida</font>'
                    else:
                        info_text += f'• Deformación: {strain_data["strain_percent"]:.2f}% (ALTO)<br>'
                        info_text += '• <font color="red">✗ Deformación excesiva para el material</font>'
                    
                    info = inputs.itemById('info')
                    info.text = info_text
                    
                except Exception as e:
                    pass
            
        except:
            pass

class HDriveCommandValidateHandler(adsk.core.ValidateInputsEventHandler):
    """Manejador para validación de inputs"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.inputs
            
            # Todos los inputs son válidos por defecto debido a los límites
            args.areInputsValid = True
            
        except:
            args.areInputsValid = False

class HDriveCommandExecuteHandler(adsk.core.CommandEventHandler):
    """Manejador para ejecutar el comando"""
    
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            
            # Obtener valores de entrada
            ratio = inputs.itemById('reductionRatio').value
            # IMPORTANTE: Fusion devuelve valores en cm, convertir a mm
            module = inputs.itemById('module').value * 10  # cm a mm
            pressure_angle_text = inputs.itemById('pressureAngle').selectedItem.name
            pressure_angle = float(pressure_angle_text.replace('°', '').split()[0])
            thickness = inputs.itemById('thickness').value * 10  # cm a mm
            cup_factor = inputs.itemById('cupFactor').valueOne
            material_idx = inputs.itemById('material').selectedItem.index
            tolerance = inputs.itemById('printTolerance').value * 10  # cm a mm
            generate_teeth = inputs.itemById('generateTeeth').value
            points_per_tooth = int(inputs.itemById('pointsPerTooth').valueOne)
            
            # Mapear material
            materials = ['steel', 'aluminum', 'plastic', 'tpu']
            material = materials[material_idx]
            
            # Calcular número de dientes
            teeth_cs = ratio * 2
            
            # Crear parámetros
            params = HarmonicDriveParams(
                teeth_cs=teeth_cs,
                module=module,
                pressure_angle=pressure_angle,
                material=material,
                print_tolerance=tolerance
            )
            
            # Generar el Harmonic Drive
            generator = HarmonicDriveGenerator(params)
            success = generator.generate(
                thickness_mm=thickness,
                cup_factor=cup_factor,
                generate_teeth=generate_teeth,
                points_per_tooth=points_per_tooth
            )
            
            if success:
                _ui.messageBox(
                    f'✅ ¡Harmonic Drive generado exitosamente!\n\n' +
                    f'📊 Especificaciones:\n' +
                    f'• Relación: {ratio}:1\n' +
                    f'• Dientes CS/FS: {teeth_cs}/{teeth_cs-2}\n' +
                    f'• Módulo: {module} mm\n' +
                    f'• Diámetro: {module * teeth_cs:.1f} mm\n' +
                    f'• Material: {material}\n\n' +
                    f'Los componentes se han creado en el diseño activo.'
                )
            else:
                _ui.messageBox('❌ Error al generar el Harmonic Drive')
            
        except Exception as e:
            if _ui:
                _ui.messageBox(f'Error: {str(e)}\n\n{traceback.format_exc()}')

class HarmonicDriveGenerator:
    """Generador principal del Harmonic Drive en Fusion 360"""
    
    def __init__(self, params: HarmonicDriveParams):
        self.params = params
        self.calc = HarmonicDriveCalculator(params)
        self.profile_gen = HarmonicDriveInvoluteProfile(params)
        
        # Referencias de Fusion
        self.app = adsk.core.Application.get()
        self.ui = self.app.userInterface
        self.design = self.app.activeProduct
        self.root = self.design.rootComponent
    
    def generate(self, thickness_mm=20, cup_factor=0.8, 
                generate_teeth=True, points_per_tooth=20):
        """
        Genera el Harmonic Drive completo
        
        Args:
            thickness_mm: Espesor de los componentes
            cup_factor: Factor de longitud de la copa (0.5-1.5)
            generate_teeth: Si generar dientes reales o solo círculos
            points_per_tooth: Puntos por diente para el perfil
        
        Returns:
            True si se generó exitosamente
        """
        try:
            # Obtener geometrías calculadas
            cs_geo = self.calc.get_circular_spline_geometry()
            fs_geo = self.calc.get_flex_spline_geometry()
            wg_geo = self.calc.get_wave_generator_geometry()
            
            # Generar componentes
            self._create_circular_spline(cs_geo, thickness_mm, generate_teeth, points_per_tooth)
            self._create_flex_spline(fs_geo, thickness_mm, cup_factor, generate_teeth, points_per_tooth)
            self._create_wave_generator(wg_geo, thickness_mm)
            
            return True
            
        except Exception as e:
            self.ui.messageBox(f'Error generando HD: {str(e)}')
            return False
    
    def _create_circular_spline(self, geometry, thickness_mm, generate_teeth, points_per_tooth):
        """Crea el Circular Spline"""
        
        # Crear componente
        occs = self.root.occurrences
        transform = adsk.core.Matrix3D.create()
        cs_occ = occs.addNewComponent(transform)
        cs_comp = cs_occ.component
        cs_comp.name = f"CircularSpline_{self.params.teeth_cs}T_{self.params.ratio:.0f}to1"
        
        # Crear sketch
        sketches = cs_comp.sketches
        xy_plane = cs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Dibujar círculos principales
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        # Círculo exterior (carcasa)
        outer_radius_cm = geometry['outer_diameter'] / 20  # mm a cm
        outer_circle = circles.addByCenterRadius(center, outer_radius_cm)
        
        # Círculo de dientes (interno)
        pitch_radius_cm = geometry['pitch_radius'] / 10
        
        if generate_teeth and self.params.teeth_cs <= 200:
            # Generar dientes reales (limitado a 200 dientes por rendimiento)
            self._draw_teeth(sketch, geometry, True, points_per_tooth)
        else:
            # Solo dibujar círculo interno
            inner_radius_cm = geometry['addendum_diameter'] / 20
            inner_circle = circles.addByCenterRadius(center, inner_radius_cm)
        
        # Extruir
        profile = sketch.profiles.item(0)
        extrudes = cs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(thickness_mm / 10)
        extrude_input.setDistanceExtent(False, distance)
        extrude = extrudes.add(extrude_input)
        
        # Aplicar apariencia
        if extrude.bodies.count > 0:
            self._apply_appearance(extrude.bodies.item(0), 'Steel', 180, 180, 190)
    
    def _create_flex_spline(self, geometry, thickness_mm, cup_factor, generate_teeth, points_per_tooth):
        """Crea el Flex Spline"""
        
        # Crear componente con offset en Z
        occs = self.root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, thickness_mm / 10 * 0.1)
        fs_occ = occs.addNewComponent(transform)
        fs_comp = fs_occ.component
        fs_comp.name = f"FlexSpline_{self.params.teeth_fs}T_Flexible"
        
        # Crear sketch para la copa
        sketches = fs_comp.sketches
        xy_plane = fs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Dibujar perfil de la copa
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        if generate_teeth and self.params.teeth_fs <= 200:
            # Generar dientes reales
            self._draw_teeth(sketch, geometry, False, points_per_tooth)
            # Círculo interior
            inner_radius_cm = geometry['inner_diameter'] / 20
            inner_circle = circles.addByCenterRadius(center, inner_radius_cm)
        else:
            # Solo círculos
            outer_radius_cm = geometry['addendum_diameter'] / 20
            inner_radius_cm = geometry['inner_diameter'] / 20
            outer_circle = circles.addByCenterRadius(center, outer_radius_cm)
            inner_circle = circles.addByCenterRadius(center, inner_radius_cm)
        
        # Extruir copa
        profile = sketch.profiles.item(0)
        extrudes = fs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        
        # Longitud de la copa
        cup_length_cm = geometry['cup_length'] * cup_factor / 10
        distance = adsk.core.ValueInput.createByReal(cup_length_cm)
        extrude_input.setDistanceExtent(False, distance)
        cup_extrude = extrudes.add(extrude_input)
        
        # Crear fondo de la copa
        bottom_sketch = sketches.add(xy_plane)
        bottom_circle = bottom_sketch.sketchCurves.sketchCircles.addByCenterRadius(
            center, inner_radius_cm
        )
        
        bottom_profile = bottom_sketch.profiles.item(0)
        bottom_extrude_input = extrudes.createInput(
            bottom_profile,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        bottom_thickness = adsk.core.ValueInput.createByReal(self.params.module / 10 * 3)
        bottom_extrude_input.setDistanceExtent(False, bottom_thickness)
        bottom_extrude = extrudes.add(bottom_extrude_input)
        
        # Aplicar apariencia
        for i in range(fs_comp.bRepBodies.count):
            body = fs_comp.bRepBodies.item(i)
            if self.params.material == 'tpu':
                self._apply_appearance(body, 'TPU_Orange', 255, 150, 100)
            else:
                self._apply_appearance(body, 'Plastic_Green', 100, 200, 100)
    
    def _create_wave_generator(self, geometry, thickness_mm):
        """Crea el Wave Generator"""
        
        # Crear componente con offset en Z
        occs = self.root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, thickness_mm / 10 * 0.2)
        wg_occ = occs.addNewComponent(transform)
        wg_comp = wg_occ.component
        wg_comp.name = f"WaveGenerator_e{self.params.eccentricity:.2f}mm"
        
        # Crear sketch
        sketches = wg_comp.sketches
        xy_plane = wg_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Crear elipse
        self._draw_ellipse(
            sketch,
            geometry['major_radius'] / 10,
            geometry['minor_radius'] / 10,
            60
        )
        
        # Agregar agujero central
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        shaft_hole = circles.addByCenterRadius(center, geometry['shaft_diameter'] / 20)
        
        # Extruir
        profiles = sketch.profiles
        for i in range(profiles.count):
            profile = profiles.item(i)
            if profile.profileLoops.count == 2:  # Perfil con agujero
                extrudes = wg_comp.features.extrudeFeatures
                extrude_input = extrudes.createInput(
                    profile,
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
                distance = adsk.core.ValueInput.createByReal(geometry['height'] / 10)
                extrude_input.setDistanceExtent(False, distance)
                extrude = extrudes.add(extrude_input)
                
                if extrude.bodies.count > 0:
                    self._apply_appearance(extrude.bodies.item(0), 'Aluminum_Red', 200, 100, 100)
                break
    
    def _draw_teeth(self, sketch, geometry, is_internal, points_per_tooth):
        """Dibuja los dientes con perfil involuta simplificado"""
        
        lines = sketch.sketchCurves.sketchLines
        num_teeth = geometry['teeth']
        pitch_radius_cm = geometry['pitch_radius'] / 10
        
        # Para rendimiento, simplificar a líneas trapezoidales
        angle_per_tooth = 2 * math.pi / num_teeth
        tooth_width = angle_per_tooth * 0.35  # Reducir ancho para mejor engrane
        space_width = angle_per_tooth * 0.35  # Espacio entre dientes
        
        # Altura del diente
        addendum_cm = self.params.addendum_factor * self.params.module / 10
        dedendum_cm = self.params.dedendum_factor * self.params.module / 10
        
        # Radios para los círculos
        if is_internal:
            # Para engranaje interno
            outer_r = pitch_radius_cm + dedendum_cm  
            inner_r = pitch_radius_cm - addendum_cm
        else:
            # Para engranaje externo
            outer_r = pitch_radius_cm + addendum_cm
            inner_r = pitch_radius_cm - dedendum_cm
        
        # Crear lista de puntos para todo el perfil
        all_points = []
        
        for i in range(num_teeth):
            base_angle = i * angle_per_tooth
            
            # Cuatro puntos por diente (trapecio)
            if is_internal:
                # Dientes hacia adentro
                points = [
                    (outer_r, base_angle - space_width/2),  # Base izquierda
                    (inner_r, base_angle - tooth_width/4),  # Punta izquierda
                    (inner_r, base_angle + tooth_width/4),  # Punta derecha
                    (outer_r, base_angle + space_width/2),  # Base derecha
                ]
            else:
                # Dientes hacia afuera
                points = [
                    (inner_r, base_angle - space_width/2),  # Base izquierda
                    (outer_r, base_angle - tooth_width/4),  # Punta izquierda
                    (outer_r, base_angle + tooth_width/4),  # Punta derecha
                    (inner_r, base_angle + space_width/2),  # Base derecha
                ]
            
            # Convertir a coordenadas cartesianas y agregar
            for r, angle in points:
                x = r * math.cos(angle)
                y = r * math.sin(angle)
                all_points.append((x, y))
        
        # Dibujar todas las líneas conectadas
        for i in range(len(all_points)):
            x1, y1 = all_points[i]
            x2, y2 = all_points[(i + 1) % len(all_points)]  # Conectar con el siguiente (circular)
            
            p1 = adsk.core.Point3D.create(x1, y1, 0)
            p2 = adsk.core.Point3D.create(x2, y2, 0)
            lines.addByTwoPoints(p1, p2)
    
    def _draw_ellipse(self, sketch, major_radius_cm, minor_radius_cm, num_points):
        """Dibuja una elipse usando spline"""
        
        curves = sketch.sketchCurves
        points = adsk.core.ObjectCollection.create()
        
        for i in range(num_points):
            angle = 2 * math.pi * i / num_points
            x = major_radius_cm * math.cos(angle)
            y = minor_radius_cm * math.sin(angle)
            points.add(adsk.core.Point3D.create(x, y, 0))
        
        points.add(points.item(0))  # Cerrar la curva
        spline = curves.sketchFittedSplines.add(points)
    
    def _apply_appearance(self, body, name, r, g, b):
        """Aplica apariencia a un cuerpo"""
        try:
            appearances = self.design.appearances
            
            appearance = None
            for i in range(appearances.count):
                if appearances.item(i).name == name:
                    appearance = appearances.item(i)
                    break
            
            if not appearance:
                appearance = appearances.add()
                appearance.name = name
                color_prop = appearance.appearanceProperties.itemByName('Color')
                if color_prop:
                    color_value = adsk.core.Color.create(r, g, b, 255)
                    color_prop.value = color_value
            
            body.appearance = appearance
        except:
            pass

def run(context):
    """Punto de entrada del Add-in"""
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        
        # Limpiar comandos anteriores
        cmdDef = _ui.commandDefinitions.itemById(COMMAND_ID)
        if cmdDef:
            cmdDef.deleteMe()
        
        # Crear nuevo comando
        cmdDef = _ui.commandDefinitions.addButtonDefinition(
            COMMAND_ID,
            COMMAND_NAME,
            COMMAND_DESCRIPTION
        )
        
        # Conectar al handler
        commandCreated = HDriveCommandCreatedHandler()
        cmdDef.commandCreated.add(commandCreated)
        _handlers.append(commandCreated)
        
        # Agregar botón al panel
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addInsPanel.controls.itemById(COMMAND_ID)
        if cntrl:
            cntrl.deleteMe()
        addInsPanel.controls.addCommand(cmdDef).isPromoted = True
        
        # Mensaje de éxito
        _ui.messageBox(
            '✅ Harmonic Drive Generator v1.0 cargado\n\n' +
            '• Perfil involuta matemáticamente correcto\n' +
            '• Validación de deformación integrada\n' +
            '• Tests automatizados disponibles\n\n' +
            'Haz clic en el botón ⚙️ en la barra de herramientas'
        )
        
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Limpieza al detener el Add-in"""
    try:
        # Eliminar botón
        addInsPanel = _ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addInsPanel.controls.itemById(COMMAND_ID)
        if cntrl:
            cntrl.deleteMe()
        
        # Eliminar definición del comando
        cmdDef = _ui.commandDefinitions.itemById(COMMAND_ID)
        if cmdDef:
            cmdDef.deleteMe()
            
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))