"""
Harmonic Drive Generator ULTIMATE - v2.0
Interfaz PRO bonita + Geometría que FUNCIONA
Lo mejor de ambos mundos!
"""
import adsk.core
import adsk.fusion
import traceback
import math

# Global variables
app = None
ui = None
handlers = []

def run(context):
    """Main entry point"""
    try:
        global app, ui
        app = adsk.core.Application.get()
        ui = app.userInterface
        
        # Create command
        cmd_defs = ui.commandDefinitions
        
        # Remove old command if exists
        existing_cmds = ['HDriveCleanCmd', 'HDriveGeneratorProCmd', 'HDriveGeneratorCmdV2', 'HDriveUltimateCmd']
        for cmd_id in existing_cmds:
            cmd_def = cmd_defs.itemById(cmd_id)
            if cmd_def:
                cmd_def.deleteMe()
        
        # Create new command
        cmd_def = cmd_defs.addButtonDefinition(
            'HDriveUltimateCmd',
            '🔧 Harmonic Drive Ultimate',
            'Professional harmonic drive generator with all features'
        )
        
        # Add command created handler
        on_command_created = CommandCreatedHandler()
        cmd_def.commandCreated.add(on_command_created)
        handlers.append(on_command_created)
        
        # Add button to panel
        panels = ui.allToolbarPanels
        panel = panels.itemById('SolidScriptsAddinsPanel')
        
        # Remove old buttons
        for ctrl in panel.controls:
            if 'HDrive' in ctrl.id:
                ctrl.deleteMe()
        
        button = panel.controls.addCommand(cmd_def)
        button.isPromoted = True
        
        ui.messageBox('🚀 Harmonic Drive Ultimate loaded!\n\nInterfaz PRO + Geometría funcional')
        
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def stop(context):
    """Clean up"""
    try:
        panel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        button = panel.controls.itemById('HDriveUltimateCmd')
        if button:
            button.deleteMe()
        
        cmd_def = ui.commandDefinitions.itemById('HDriveUltimateCmd')
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
            cmd.isRepeatable = False
            inputs = cmd.commandInputs
            
            # Title
            inputs.addTextBoxCommandInput('title', '', 
                '<b style="font-size: 14px">🔧 Harmonic Drive Generator Ultimate</b><br>' +
                '<i>Versión 2.0 - Interfaz PRO + Geometría Funcional</i>', 
                2, True)
            
            # ========== BASIC PARAMETERS GROUP ==========
            basic_group = inputs.addGroupCommandInput('basic_group', '⚙️ Parámetros Básicos')
            basic_group.isExpanded = True
            basic_inputs = basic_group.children
            
            # Module
            module_input = basic_inputs.addFloatSpinnerCommandInput(
                'module', 'Módulo (mm)', 'mm', 0.5, 2.0, 0.1, 1.0
            )
            module_input.tooltip = 'Tamaño del diente (0.5-2.0mm)'
            
            # Teeth
            teeth_input = basic_inputs.addIntegerSpinnerCommandInput(
                'teeth_cs', 'Dientes (Circular Spline)', 60, 200, 2, 100
            )
            teeth_input.tooltip = 'Número de dientes (debe ser par, 60-200)'
            
            # Info display
            basic_inputs.addTextBoxCommandInput(
                'info_display', '', 
                '<b>Relación de Reducción:</b> 50:1<br>' +
                '<b>Dientes Flex Spline:</b> 98<br>' +
                '<b>Excentricidad:</b> 0.32mm', 
                3, True
            )
            
            # ========== MOTOR MOUNTING GROUP ==========
            motor_group = inputs.addGroupCommandInput('motor_group', '🔌 Montaje de Motor')
            motor_group.isExpanded = True
            motor_inputs = motor_group.children
            
            # Enable motor mount
            motor_enabled = motor_inputs.addBoolValueInput(
                'motor_enabled', 'Agregar montaje para motor', True, '', True
            )
            
            # Motor type
            motor_type = motor_inputs.addDropDownCommandInput(
                'motor_type', 'Tipo de Motor', 
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            motor_type.listItems.add('NEMA 14 (35mm)', False)
            motor_type.listItems.add('NEMA 17 (42mm)', True)  # Default
            motor_type.listItems.add('NEMA 23 (57mm)', False)
            motor_type.listItems.add('NEMA 34 (86mm)', False)
            motor_type.tooltip = 'Tamaño estándar del motor NEMA'
            
            # Shaft coupling
            coupling_type = motor_inputs.addDropDownCommandInput(
                'coupling_type', 'Tipo de Acople',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            coupling_type.listItems.add('Prisionero (Set Screw)', True)
            coupling_type.listItems.add('Abrazadera (Clamp)', False)
            coupling_type.listItems.add('Chaveta (Keyway)', False)
            
            # ========== OUTPUT SHAFT GROUP ==========
            output_group = inputs.addGroupCommandInput('output_group', '🔄 Eje de Salida')
            output_group.isExpanded = True
            output_inputs = output_group.children
            
            # Shaft diameter
            shaft_dia = output_inputs.addFloatSpinnerCommandInput(
                'shaft_diameter', 'Diámetro del Eje (mm)', 'mm', 
                5.0, 20.0, 1.0, 8.0
            )
            shaft_dia.tooltip = 'Diámetro del eje de salida'
            
            # Shaft length
            shaft_len = output_inputs.addFloatSpinnerCommandInput(
                'shaft_length', 'Longitud del Eje (mm)', 'mm', 
                10.0, 50.0, 5.0, 30.0
            )
            
            # Bearing type
            bearing_type = output_inputs.addDropDownCommandInput(
                'bearing_type', 'Rodamiento',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            bearing_type.listItems.add('608ZZ (22x8x7mm)', True)
            bearing_type.listItems.add('6900 (22x10x6mm)', False)
            bearing_type.listItems.add('6801 (21x12x5mm)', False)
            bearing_type.listItems.add('Sin rodamiento', False)
            
            # ========== LUBRICATION GROUP ==========
            lube_group = inputs.addGroupCommandInput('lube_group', '💧 Lubricación')
            lube_group.isExpanded = False
            lube_inputs = lube_group.children
            
            # Enable grease pockets
            grease_enabled = lube_inputs.addBoolValueInput(
                'grease_enabled', 'Agregar bolsillos para grasa', True, '', True
            )
            grease_enabled.tooltip = '¡Importante para que funcione suave!'
            
            # Grease pocket size
            pocket_size = lube_inputs.addDropDownCommandInput(
                'pocket_size', 'Tamaño de Bolsillos',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            pocket_size.listItems.add('Pequeños (1mm)', False)
            pocket_size.listItems.add('Medianos (2mm)', True)
            pocket_size.listItems.add('Grandes (3mm)', False)
            
            # Grease nipple
            nipple_enabled = lube_inputs.addBoolValueInput(
                'nipple_enabled', 'Agregar grasera/nipple', True, '', False
            )
            
            # ========== 3D PRINTING GROUP ==========
            print_group = inputs.addGroupCommandInput('print_group', '🖨️ Impresión 3D')
            print_group.isExpanded = False
            print_inputs = print_group.children
            
            # Print tolerance
            tolerance = print_inputs.addFloatSpinnerCommandInput(
                'print_tolerance', 'Tolerancia (mm)', 'mm', 
                0.0, 0.5, 0.05, 0.2
            )
            tolerance.tooltip = 'Clearance para piezas impresas en 3D'
            
            # Material
            material = print_inputs.addDropDownCommandInput(
                'material', 'Material',
                adsk.core.DropDownStyles.TextListDropDownStyle
            )
            material.listItems.add('PLA (rígido)', False)
            material.listItems.add('PETG (balanceado)', True)
            material.listItems.add('TPU 95A (flexible para FS)', False)
            material.listItems.add('Nylon (duradero)', False)
            
            # ========== ADVANCED GROUP ==========
            advanced_group = inputs.addGroupCommandInput('advanced_group', '🔬 Avanzado')
            advanced_group.isExpanded = False
            advanced_inputs = advanced_group.children
            
            # Wall thickness
            wall = advanced_inputs.addFloatSpinnerCommandInput(
                'wall_thickness', 'Espesor de Pared (mm)', 'mm', 
                2.0, 5.0, 0.5, 3.0
            )
            
            # Wave lobes
            lobes = advanced_inputs.addIntegerSpinnerCommandInput(
                'wave_lobes', 'Lóbulos del Wave Generator', 
                2, 3, 1, 2
            )
            lobes.tooltip = 'Normalmente 2 para harmonic drive estándar'
            
            # Flex slots
            flex_slots = advanced_inputs.addBoolValueInput(
                'flex_slots', 'Agregar ranuras de flexibilidad', True, '', True
            )
            
            # Status
            inputs.addTextBoxCommandInput('status', '', 
                '<b>Estado:</b> <font color="green">✓ Listo para generar</font>', 
                1, True)
            
            # Add handlers
            on_execute = CommandExecuteHandler()
            cmd.execute.add(on_execute)
            handlers.append(on_execute)
            
            on_input_changed = InputChangedHandler()
            cmd.inputChanged.add(on_input_changed)
            handlers.append(on_input_changed)
            
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class InputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.inputs
            changed = args.input
            
            # Update info when teeth change
            if changed.id == 'teeth_cs':
                teeth_cs = int(inputs.itemById('teeth_cs').value)
                teeth_fs = teeth_cs - 2
                ratio = teeth_cs // 2
                
                # Get module for eccentricity calculation
                module_raw = inputs.itemById('module').value
                module = module_raw * 10 if module_raw < 0.3 else module_raw
                eccentricity = (2 * module) / math.pi
                
                info = inputs.itemById('info_display')
                info.text = (
                    f'<b>Relación de Reducción:</b> {ratio}:1<br>'
                    f'<b>Dientes Flex Spline:</b> {teeth_fs}<br>'
                    f'<b>Excentricidad:</b> {eccentricity:.2f}mm'
                )
            
            # Enable/disable motor options
            elif changed.id == 'motor_enabled':
                enabled = inputs.itemById('motor_enabled').value
                inputs.itemById('motor_type').isEnabled = enabled
                inputs.itemById('coupling_type').isEnabled = enabled
            
            # Enable/disable grease options
            elif changed.id == 'grease_enabled':
                enabled = inputs.itemById('grease_enabled').value
                inputs.itemById('pocket_size').isEnabled = enabled
                inputs.itemById('nipple_enabled').isEnabled = enabled
                
        except:
            pass

class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    
    def notify(self, args):
        try:
            inputs = args.command.commandInputs
            
            # Get all parameters
            params = self.get_parameters(inputs)
            
            # Create the geometry
            success = create_harmonic_drive_ultimate(params)
            
            if success:
                ui.messageBox(
                    '✅ ¡Harmonic Drive Ultimate creado!\n\n' +
                    f'📊 Especificaciones:\n' +
                    f'• Módulo: {params["module"]}mm\n' +
                    f'• Relación: {params["ratio"]}:1\n' +
                    f'• Motor: {params["motor_type"] if params["motor_enabled"] else "No"}\n' +
                    f'• Lubricación: {"Sí" if params["grease_enabled"] else "No"}\n' +
                    f'• Tolerancia 3D: {params["print_tolerance"]}mm'
                )
            
        except Exception as e:
            ui.messageBox(f'Error: {str(e)}\n\n{traceback.format_exc()}')
    
    def get_parameters(self, inputs):
        """Extract all parameters from inputs"""
        # Get module with conversion
        module_raw = inputs.itemById('module').value
        module = module_raw * 10 if module_raw < 0.3 else module_raw
        
        # Get teeth
        teeth_cs = int(inputs.itemById('teeth_cs').value)
        teeth_fs = teeth_cs - 2
        
        # Get shaft diameter with conversion
        shaft_raw = inputs.itemById('shaft_diameter').value
        shaft_dia = shaft_raw * 10 if shaft_raw < 2 else shaft_raw
        
        # Get shaft length with conversion
        length_raw = inputs.itemById('shaft_length').value
        shaft_len = length_raw * 10 if length_raw < 5 else length_raw
        
        return {
            'module': module,
            'teeth_cs': teeth_cs,
            'teeth_fs': teeth_fs,
            'ratio': teeth_cs // 2,
            'motor_enabled': inputs.itemById('motor_enabled').value,
            'motor_type': inputs.itemById('motor_type').selectedItem.name if inputs.itemById('motor_enabled').value else None,
            'coupling_type': inputs.itemById('coupling_type').selectedItem.name,
            'shaft_diameter': shaft_dia,
            'shaft_length': shaft_len,
            'bearing_type': inputs.itemById('bearing_type').selectedItem.name,
            'grease_enabled': inputs.itemById('grease_enabled').value,
            'pocket_size': inputs.itemById('pocket_size').selectedItem.name if inputs.itemById('grease_enabled').value else None,
            'nipple_enabled': inputs.itemById('nipple_enabled').value,
            'print_tolerance': inputs.itemById('print_tolerance').value * 10 if inputs.itemById('print_tolerance').value < 0.1 else inputs.itemById('print_tolerance').value,
            'material': inputs.itemById('material').selectedItem.name,
            'wall_thickness': inputs.itemById('wall_thickness').value * 10 if inputs.itemById('wall_thickness').value < 1 else inputs.itemById('wall_thickness').value,
            'wave_lobes': int(inputs.itemById('wave_lobes').value),
            'flex_slots': inputs.itemById('flex_slots').value
        }

def create_harmonic_drive_ultimate(params):
    """Create the harmonic drive with all features"""
    try:
        design = app.activeProduct
        root = design.rootComponent
        
        # Calculate dimensions
        pitch_dia_cs = params['module'] * params['teeth_cs']
        pitch_dia_fs = params['module'] * params['teeth_fs']
        eccentricity = (2 * params['module']) / math.pi
        
        # Create components
        cs_success = create_circular_spline_ultimate(root, params, pitch_dia_cs)
        fs_success = create_flex_spline_ultimate(root, params, pitch_dia_fs)
        wg_success = create_wave_generator_ultimate(root, params, pitch_dia_fs, eccentricity)
        
        return cs_success and fs_success and wg_success
        
    except Exception as e:
        ui.messageBox(f'Error creating geometry: {str(e)}')
        return False

def create_circular_spline_ultimate(root, params, pitch_dia):
    """Create circular spline with all features"""
    try:
        # Create component
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        cs_occ = occs.addNewComponent(transform)
        cs_comp = cs_occ.component
        cs_comp.name = f"CircularSpline_{params['teeth_cs']}T_{params['ratio']}to1"
        
        # Create main body
        sketches = cs_comp.sketches
        xy_plane = cs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        # Apply print tolerance
        inner_radius_cm = (pitch_dia / 10) + (params['print_tolerance'] / 10)
        outer_radius_cm = inner_radius_cm + (params['wall_thickness'] / 10)
        
        outer_circle = circles.addByCenterRadius(center, outer_radius_cm)
        inner_circle = circles.addByCenterRadius(center, inner_radius_cm)
        
        # Add teeth representation
        if params['teeth_cs'] <= 100:
            add_teeth_pattern(sketch, inner_radius_cm, params['teeth_cs'], True, params['module'] / 10)
        
        # Add motor mounting holes if enabled
        if params['motor_enabled']:
            add_motor_holes(sketch, params['motor_type'])
        
        # Add grease pockets if enabled
        if params['grease_enabled']:
            add_grease_pockets(sketch, inner_radius_cm, params['pocket_size'])
        
        # Extrude
        profile = sketch.profiles.item(0)
        extrudes = cs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        distance = adsk.core.ValueInput.createByReal(4.0)  # 40mm
        extrude_input.setDistanceExtent(False, distance)
        extrude = extrudes.add(extrude_input)
        
        # Apply appearance
        if extrude.bodies.count > 0:
            apply_appearance(extrude.bodies.item(0), "Steel_CS", 180, 180, 200)
        
        return True
        
    except Exception as e:
        ui.messageBox(f'Error in CS: {str(e)}')
        return False

def create_flex_spline_ultimate(root, params, pitch_dia):
    """Create flex spline with all features"""
    try:
        # Create component with offset
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, 0.3)  # 3mm offset
        fs_occ = occs.addNewComponent(transform)
        fs_comp = fs_occ.component
        fs_comp.name = f"FlexSpline_{params['teeth_fs']}T_Flexible"
        
        # Create cup body
        sketches = fs_comp.sketches
        xy_plane = fs_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        # Apply print tolerance
        outer_radius_cm = (pitch_dia / 10) - (params['print_tolerance'] / 10)
        wall_thickness_cm = params['module'] / 10 * 1.5  # 1.5x module for flex
        inner_radius_cm = outer_radius_cm - wall_thickness_cm
        
        outer_circle = circles.addByCenterRadius(center, outer_radius_cm)
        inner_circle = circles.addByCenterRadius(center, inner_radius_cm)
        
        # Add teeth representation
        if params['teeth_fs'] <= 100:
            add_teeth_pattern(sketch, outer_radius_cm, params['teeth_fs'], False, params['module'] / 10)
        
        # Add flex slots if enabled
        if params['flex_slots']:
            add_flex_slots(sketch, outer_radius_cm, inner_radius_cm)
        
        # Extrude cup walls
        profile = sketch.profiles.item(0)
        extrudes = fs_comp.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation
        )
        cup_height = 5.0  # 50mm
        distance = adsk.core.ValueInput.createByReal(cup_height)
        extrude_input.setDistanceExtent(False, distance)
        cup_extrude = extrudes.add(extrude_input)
        
        # Add bottom
        add_cup_bottom(fs_comp, inner_radius_cm, params)
        
        # Add output shaft if specified
        if params['shaft_diameter'] > 0:
            add_output_shaft(fs_comp, params, cup_height)
        
        # Apply flexible appearance
        for i in range(fs_comp.bRepBodies.count):
            body = fs_comp.bRepBodies.item(i)
            if 'TPU' in params['material']:
                apply_appearance(body, "FlexTPU", 255, 150, 100)
            else:
                apply_appearance(body, "FlexGreen", 100, 200, 100)
        
        return True
        
    except Exception as e:
        ui.messageBox(f'Error in FS: {str(e)}')
        return False

def create_wave_generator_ultimate(root, params, base_dia, eccentricity):
    """Create wave generator with all features"""
    try:
        # Create component with offset
        occs = root.occurrences
        transform = adsk.core.Matrix3D.create()
        transform.translation = adsk.core.Vector3D.create(0, 0, 0.6)  # 6mm offset
        wg_occ = occs.addNewComponent(transform)
        wg_comp = wg_occ.component
        wg_comp.name = f"WaveGenerator_{params['wave_lobes']}Lobe"
        
        # Create sketch
        sketches = wg_comp.sketches
        xy_plane = wg_comp.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        # Create ellipse or multi-lobe shape
        base_radius_cm = (base_dia / 10) - 0.3  # Slightly smaller than FS
        ecc_cm = eccentricity / 10
        
        if params['wave_lobes'] == 2:
            # Standard ellipse
            create_ellipse(sketch, base_radius_cm + ecc_cm, base_radius_cm - ecc_cm * 0.5)
        else:
            # 3-lobe version
            create_trilobe(sketch, base_radius_cm, ecc_cm)
        
        # Add center hole for motor
        add_motor_shaft_hole(sketch, params)
        
        # Extrude
        profiles = sketch.profiles
        for i in range(profiles.count):
            profile = profiles.item(i)
            if profile.profileLoops.count == 2:  # Profile with hole
                extrudes = wg_comp.features.extrudeFeatures
                extrude_input = extrudes.createInput(
                    profile,
                    adsk.fusion.FeatureOperations.NewBodyFeatureOperation
                )
                distance = adsk.core.ValueInput.createByReal(2.5)  # 25mm
                extrude_input.setDistanceExtent(False, distance)
                extrude = extrudes.add(extrude_input)
                
                # Apply appearance
                if extrude.bodies.count > 0:
                    apply_appearance(extrude.bodies.item(0), "Aluminum_WG", 200, 100, 100)
                break
        
        return True
        
    except Exception as e:
        ui.messageBox(f'Error in WG: {str(e)}')
        return False

# ========== HELPER FUNCTIONS ==========

def add_teeth_pattern(sketch, radius, num_teeth, is_internal, module_cm):
    """Add visual teeth pattern"""
    try:
        lines = sketch.sketchCurves.sketchLines
        tooth_height = module_cm * 0.8
        
        for i in range(min(num_teeth, 60)):  # Limit for performance
            angle = 2 * math.pi * i / num_teeth
            x1 = radius * math.cos(angle)
            y1 = radius * math.sin(angle)
            
            if is_internal:
                r2 = radius + tooth_height
            else:
                r2 = radius - tooth_height
            
            x2 = r2 * math.cos(angle)
            y2 = r2 * math.sin(angle)
            
            p1 = adsk.core.Point3D.create(x1, y1, 0)
            p2 = adsk.core.Point3D.create(x2, y2, 0)
            lines.addByTwoPoints(p1, p2)
    except:
        pass

def add_motor_holes(sketch, motor_type):
    """Add NEMA motor mounting holes"""
    try:
        circles = sketch.sketchCurves.sketchCircles
        
        # NEMA bolt patterns (in mm)
        patterns = {
            'NEMA 14': {'bolt_circle': 26, 'bolt_size': 3},
            'NEMA 17': {'bolt_circle': 31, 'bolt_size': 3},
            'NEMA 23': {'bolt_circle': 47.14, 'bolt_size': 5},
            'NEMA 34': {'bolt_circle': 69.6, 'bolt_size': 6}
        }
        
        # Get pattern for motor type
        pattern = None
        for key in patterns:
            if key in motor_type:
                pattern = patterns[key]
                break
        
        if pattern:
            bc_cm = pattern['bolt_circle'] / 10
            hole_radius_cm = pattern['bolt_size'] / 20
            
            # Add 4 holes
            for angle in [45, 135, 225, 315]:
                rad = math.radians(angle)
                x = bc_cm * math.cos(rad) / math.sqrt(2)
                y = bc_cm * math.sin(rad) / math.sqrt(2)
                center = adsk.core.Point3D.create(x, y, 0)
                circles.addByCenterRadius(center, hole_radius_cm)
    except:
        pass

def add_grease_pockets(sketch, radius, size):
    """Add grease pockets"""
    try:
        circles = sketch.sketchCurves.sketchCircles
        
        sizes = {
            'Pequeños': 0.05,  # 0.5mm radius
            'Medianos': 0.1,   # 1mm radius
            'Grandes': 0.15    # 1.5mm radius
        }
        
        pocket_radius = sizes.get(size.split()[0], 0.1)
        
        # Add 8 pockets
        for i in range(8):
            angle = 2 * math.pi * i / 8
            x = (radius - 0.2) * math.cos(angle)
            y = (radius - 0.2) * math.sin(angle)
            center = adsk.core.Point3D.create(x, y, 0)
            circles.addByCenterRadius(center, pocket_radius)
    except:
        pass

def add_flex_slots(sketch, outer_r, inner_r):
    """Add flexibility slots"""
    try:
        lines = sketch.sketchCurves.sketchLines
        
        # Add 8 radial slots
        for i in range(8):
            angle = 2 * math.pi * i / 8
            
            # Slot endpoints
            x1 = inner_r * math.cos(angle)
            y1 = inner_r * math.sin(angle)
            x2 = (outer_r - 0.05) * math.cos(angle)
            y2 = (outer_r - 0.05) * math.sin(angle)
            
            p1 = adsk.core.Point3D.create(x1, y1, 0)
            p2 = adsk.core.Point3D.create(x2, y2, 0)
            lines.addByTwoPoints(p1, p2)
    except:
        pass

def add_cup_bottom(component, inner_radius, params):
    """Add bottom to flex spline cup"""
    try:
        sketches = component.sketches
        xy_plane = component.xYConstructionPlane
        sketch = sketches.add(xy_plane)
        
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        circle = circles.addByCenterRadius(center, inner_radius)
        
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        
        thickness = params['module'] / 10 * 3  # 3x module thickness
        distance = adsk.core.ValueInput.createByReal(thickness)
        extrude_input.setDistanceExtent(False, distance)
        extrudes.add(extrude_input)
    except:
        pass

def add_output_shaft(component, params, cup_height):
    """Add output shaft to flex spline"""
    try:
        # Create construction plane at top of cup
        planes = component.constructionPlanes
        plane_input = planes.createInput()
        offset_value = adsk.core.ValueInput.createByReal(cup_height)
        plane_input.setByOffset(component.xYConstructionPlane, offset_value)
        top_plane = planes.add(plane_input)
        
        # Create shaft sketch
        sketches = component.sketches
        sketch = sketches.add(top_plane)
        
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        shaft_radius_cm = params['shaft_diameter'] / 20
        circle = circles.addByCenterRadius(center, shaft_radius_cm)
        
        # Extrude shaft
        profile = sketch.profiles.item(0)
        extrudes = component.features.extrudeFeatures
        extrude_input = extrudes.createInput(
            profile,
            adsk.fusion.FeatureOperations.JoinFeatureOperation
        )
        
        shaft_length_cm = params['shaft_length'] / 10
        distance = adsk.core.ValueInput.createByReal(shaft_length_cm)
        extrude_input.setDistanceExtent(False, distance)
        extrudes.add(extrude_input)
    except:
        pass

def add_motor_shaft_hole(sketch, params):
    """Add motor shaft hole"""
    try:
        circles = sketch.sketchCurves.sketchCircles
        center = adsk.core.Point3D.create(0, 0, 0)
        
        # Standard NEMA shaft sizes (mm)
        shaft_sizes = {
            'NEMA 14': 5,
            'NEMA 17': 5,
            'NEMA 23': 6.35,
            'NEMA 34': 14
        }
        
        shaft_dia = 5  # Default
        if params['motor_enabled'] and params['motor_type']:
            for key in shaft_sizes:
                if key in params['motor_type']:
                    shaft_dia = shaft_sizes[key]
                    break
        
        # Add print tolerance
        shaft_radius_cm = (shaft_dia / 20) + (params['print_tolerance'] / 10)
        circles.addByCenterRadius(center, shaft_radius_cm)
    except:
        pass

def create_ellipse(sketch, major_r, minor_r):
    """Create ellipse shape"""
    try:
        curves = sketch.sketchCurves
        points = adsk.core.ObjectCollection.create()
        
        for i in range(60):
            angle = 2 * math.pi * i / 60
            x = major_r * math.cos(angle)
            y = minor_r * math.sin(angle)
            points.add(adsk.core.Point3D.create(x, y, 0))
        
        points.add(points.item(0))
        spline = curves.sketchFittedSplines.add(points)
    except:
        pass

def create_trilobe(sketch, base_r, ecc):
    """Create 3-lobe shape"""
    try:
        curves = sketch.sketchCurves
        points = adsk.core.ObjectCollection.create()
        
        for i in range(90):
            angle = 2 * math.pi * i / 90
            # 3-lobe formula
            r = base_r + ecc * math.cos(3 * angle)
            x = r * math.cos(angle)
            y = r * math.sin(angle)
            points.add(adsk.core.Point3D.create(x, y, 0))
        
        points.add(points.item(0))
        spline = curves.sketchFittedSplines.add(points)
    except:
        pass

def apply_appearance(body, name, r, g, b):
    """Apply appearance to body"""
    try:
        design = app.activeProduct
        appearances = design.appearances
        
        appearance = None
        for i in range(appearances.count):
            if appearances.item(i).name == name:
                appearance = appearances.item(i)
                break
        
        if not appearance:
            appearance = appearances.add()
            appearance.name = name
            color_prop = appearance.appearanceProperties.itemByName("Color")
            if color_prop:
                color_value = adsk.core.Color.create(r, g, b, 255)
                color_prop.value = color_value
        
        body.appearance = appearance
    except:
        pass