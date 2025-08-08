# 📐 FÓRMULAS COMPLETAS DEL HARMONIC DRIVE

## 1. COMPONENTES PRINCIPALES

### 1.1 Circular Spline (CS) - Anillo Rígido
- **Tipo**: Engranaje interno (dientes hacia adentro)
- **Material**: Rígido (acero, aluminio)
- **Fijo o rotatorio**: Depende del diseño

### 1.2 Flex Spline (FS) - Copa Flexible
- **Tipo**: Engranaje externo (dientes hacia afuera)
- **Material**: Flexible (acero delgado, plástico)
- **Forma**: Copa con fondo cerrado

### 1.3 Wave Generator (WG) - Generador de Onda
- **Tipo**: Leva elíptica
- **Función**: Deforma el FS para que engrane con CS
- **Rotación**: Entrada del sistema

## 2. FÓRMULAS FUNDAMENTALES

### 2.1 Relación de Dientes
```
Z_fs = Z_cs - 2
```
Donde:
- Z_fs = Número de dientes del Flex Spline
- Z_cs = Número de dientes del Circular Spline
- La diferencia SIEMPRE es 2 para un harmonic drive estándar

### 2.2 Relación de Reducción
```
i = Z_cs / (Z_cs - Z_fs) = Z_cs / 2
```
O también:
```
i = -Z_fs / (Z_cs - Z_fs) = -Z_fs / 2
```
El signo negativo indica inversión de dirección

### 2.3 Módulo del Engranaje
```
m = D_p / Z
```
Donde:
- m = módulo (mm)
- D_p = diámetro primitivo (mm)
- Z = número de dientes

## 3. GEOMETRÍA DEL DIENTE

### 3.1 Perfil Involuta
```python
# Coordenadas paramétricas de la involuta
x(t) = r_b * (cos(t) + t * sin(t))
y(t) = r_b * (sin(t) - t * cos(t))
```
Donde:
- r_b = radio base = r_p * cos(α)
- r_p = radio primitivo
- α = ángulo de presión (típicamente 20° o 30° para HD)
- t = parámetro (0 a t_max)

### 3.2 Dimensiones del Diente
```
h_a = k_a * m        # Altura del diente (addendum)
h_f = k_f * m        # Profundidad del diente (dedendum)
h = h_a + h_f        # Altura total del diente
s = (π * m) / 2      # Espesor del diente en el círculo primitivo
```

Valores típicos para Harmonic Drive:
- k_a = 0.8 (reducido para evitar interferencia)
- k_f = 1.0
- Ángulo de presión α = 30° (mayor que el estándar de 20°)

### 3.3 Diámetros
```
D_p = m * Z                    # Diámetro primitivo
D_a = D_p + 2 * h_a           # Diámetro exterior (addendum)
D_f = D_p - 2 * h_f           # Diámetro raíz (dedendum)
D_b = D_p * cos(α)            # Diámetro base
```

## 4. WAVE GENERATOR (ELIPSE)

### 4.1 Excentricidad
```
e = (ΔZ * m) / π = (2 * m) / π
```
Esta es la diferencia radial entre el eje mayor y menor de la elipse

### 4.2 Dimensiones de la Elipse
```
a = r_fs - clearance + e      # Semi-eje mayor
b = r_fs - clearance - e      # Semi-eje menor
```
Donde:
- r_fs = radio interior del Flex Spline
- clearance = holgura (típicamente 0.1-0.2mm)

### 4.3 Deformación del Flex Spline
```
w_max = 2 * e                  # Deformación radial máxima
ε = w_max / r_fs              # Strain (deformación relativa)
```
Límite típico: ε < 0.003 (0.3%) para acero

## 5. CÁLCULOS DE DISEÑO

### 5.1 Selección del Módulo
```
m_min = T / (k * Z_fs * σ_allow)
```
Donde:
- T = torque de salida (N·mm)
- k = factor de diseño (~500-1000)
- σ_allow = esfuerzo permisible del material (MPa)

### 5.2 Espesor de Pared del Flex Spline
```
t_fs = k_t * m
```
Típicamente: k_t = 1.5 a 2.0

### 5.3 Longitud de la Copa del Flex Spline
```
L_fs = k_L * D_p
```
Típicamente: k_L = 0.8 a 1.2

## 6. VALIDACIONES CRÍTICAS

### 6.1 Número Mínimo de Dientes (evitar socavado)
```
Z_min = 2 / (sin²(α))
```
Para α = 20°: Z_min ≈ 17
Para α = 30°: Z_min ≈ 8

### 6.2 Relación de Contacto
```
ε_α = (√(r_a²-r_b²) - √(r_p²-r_b²)) / (π * m * cos(α))
```
Debe ser > 1.2 para transmisión suave

### 6.3 Backlash (Juego)
```
j_t = 0.04 * m  a  0.06 * m     # Juego tangencial
j_r = j_t / (2 * tan(α))        # Juego radial
```

## 7. EJEMPLO DE CÁLCULO COMPLETO

### Dados:
- Relación de reducción deseada: 100:1
- Módulo: 0.5 mm
- Material: Acero (E = 200 GPa, σ_y = 250 MPa)

### Cálculos:
```
1. Número de dientes:
   Z_cs = 2 * i = 2 * 100 = 200
   Z_fs = Z_cs - 2 = 198

2. Diámetros primitivos:
   D_p_cs = 0.5 * 200 = 100 mm
   D_p_fs = 0.5 * 198 = 99 mm

3. Excentricidad del WG:
   e = (2 * 0.5) / π = 0.318 mm

4. Dimensiones del diente (α = 30°):
   h_a = 0.8 * 0.5 = 0.4 mm
   h_f = 1.0 * 0.5 = 0.5 mm
   
5. Diámetros finales CS:
   D_a_cs = 100 - 2*0.4 = 99.2 mm (interno)
   D_f_cs = 100 + 2*0.5 = 101 mm (interno)
   
6. Diámetros finales FS:
   D_a_fs = 99 + 2*0.4 = 99.8 mm (externo)
   D_f_fs = 99 - 2*0.5 = 98 mm (externo)

7. Espesor pared FS:
   t_fs = 1.5 * 0.5 = 0.75 mm

8. Deformación máxima:
   ε = 0.636/49.5 = 0.0128 = 1.28% (¡MUY ALTO!)
   Necesita material más flexible o mayor diámetro
```

## 8. FACTORES DE CORRECCIÓN PARA IMPRESIÓN 3D

### 8.1 Tolerancias
```
Δ_print = 0.1 a 0.3 mm          # Tolerancia de impresión
m_effective = m + Δ_print        # Módulo efectivo
```

### 8.2 Modificaciones del Perfil
```
tip_relief = 0.1 * m            # Alivio en la punta
root_relief = 0.05 * m          # Alivio en la raíz
```

### 8.3 Material
- PLA: Rígido, bueno para CS y WG
- PETG: Balance, bueno para todas las piezas
- TPU 95A: Flexible, ideal para FS
- Nylon: Duradero, bajo fricción

## 9. VERIFICACIÓN FINAL

### Checklist de Diseño:
- [ ] Z_cs es par
- [ ] Z_fs = Z_cs - 2
- [ ] e = (2 * m) / π
- [ ] ε < 0.3% para acero, < 2% para plástico
- [ ] Relación de contacto > 1.2
- [ ] Sin interferencia entre dientes
- [ ] Backlash apropiado (0.04-0.06 * m)
- [ ] Espesor FS permite flexión sin rotura

## 10. CÓDIGO DE VALIDACIÓN

```python
def validate_harmonic_drive(Z_cs, module, material='steel'):
    """Valida los parámetros del Harmonic Drive"""
    
    # Cálculos básicos
    Z_fs = Z_cs - 2
    ratio = Z_cs / 2
    e = (2 * module) / math.pi
    D_p_fs = module * Z_fs
    
    # Validaciones
    errors = []
    
    if Z_cs % 2 != 0:
        errors.append("Z_cs debe ser par")
    
    if Z_cs < 60:
        errors.append("Z_cs muy pequeño, mínimo 60")
    
    if Z_cs > 320:
        errors.append("Z_cs muy grande, máximo 320")
    
    # Verificar deformación
    strain = (2 * e) / (D_p_fs / 2)
    max_strain = 0.003 if material == 'steel' else 0.02
    
    if strain > max_strain:
        errors.append(f"Deformación {strain:.3f} > máximo {max_strain}")
    
    return len(errors) == 0, errors
```

---

**IMPORTANTE**: Estas fórmulas son la BASE MATEMÁTICA CORRECTA para el Harmonic Drive. 
Cualquier implementación debe seguir estas ecuaciones EXACTAMENTE.