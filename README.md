# 🔧 Harmonic Drive Generator for Fusion 360

[![Fusion 360](https://img.shields.io/badge/Fusion%20360-API-orange)](https://www.autodesk.com/products/fusion-360)
[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow)](DEVELOPMENT_PLAN.md)

Professional parametric generator for Harmonic Drives (Strain Wave Gears) optimized for 3D printing and robotics applications.

## 🎯 What is a Harmonic Drive?

A Harmonic Drive is a high-precision gear mechanism that achieves high reduction ratios (30:1 to 320:1) in a compact space. It consists of three main components:

1. **Circular Spline (CS)** - Rigid ring with internal teeth
2. **Flex Spline (FS)** - Flexible cup with external teeth (2 fewer teeth than CS)
3. **Wave Generator (WG)** - Elliptical cam that deforms the Flex Spline

## ✨ Features

### Current (v0.1.0-alpha)
- ✅ Basic 3-component generation
- ✅ Simple UI interface
- ✅ Parametric design
- ✅ STL export ready

### In Development
- 🚧 True involute tooth profiles
- 🚧 Mesh validation
- 🚧 Interference checking
- 🚧 Material-specific tolerances
- 🚧 Automated testing suite

### Planned
- 📋 Planetary gear sets
- 📋 NEMA motor mounts
- 📋 ISO 9409-1 flanges
- 📋 Complete robotics library

## 📦 Installation

### Method 1: Direct Installation
1. Download this repository as ZIP
2. Extract to: `%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns\`
3. Restart Fusion 360
4. Go to `Utilities > Add-Ins > Scripts and Add-Ins`
5. Select "HarmonicDriveGenerator" and click "Run"

### Method 2: Git Clone (Recommended for developers)
```bash
cd "%appdata%\Autodesk\Autodesk Fusion 360\API\AddIns"
git clone https://github.com/yourusername/HarmonicDriveGenerator.git
```

## 🚀 Quick Start

### Generate a Simple Harmonic Drive
```python
from fusion_lib import SimpleGear

# Create gear generator
gear_gen = SimpleGear()

# Generate a harmonic drive with 100:1 reduction
gear_gen.crear_engranaje_spur(
    num_dientes=100,
    modulo_mm=1.0,
    espesor_mm=20.0
)
```

### Using the UI
1. Click the "🔧 Harmonic Drive" button in the toolbar
2. Set your parameters:
   - Module: 0.5-2.0mm (tooth size)
   - Teeth: 60-200 (must be even)
   - Thickness: Component thickness
3. Click "OK" to generate

## 📐 Key Parameters

| Parameter | Range | Default | Description |
|-----------|-------|---------|-------------|
| Module | 0.5-2.0mm | 1.0mm | Tooth size |
| Teeth (CS) | 60-200 | 100 | Number of teeth (even) |
| Thickness | 5-50mm | 20mm | Component thickness |
| Pressure Angle | 20-30° | 30° | Tooth pressure angle |

### Critical Formulas
```
Teeth_FS = Teeth_CS - 2
Reduction_Ratio = Teeth_CS / 2
Eccentricity = (2 × Module) / π
```

## 🏗️ Project Structure

```
HarmonicDriveGenerator/
├── fusion_lib/          # Core library
│   ├── fusion_utils.py  # API wrapper
│   └── gears.py         # Gear generators
├── HDriveGenerator.py   # Main add-in
├── HDriveSimple.py      # Simplified version
├── test_simple_gear.py  # Test script
└── docs/                # Documentation
```

## 🧪 Testing

Run tests from Fusion 360:
```
Utilities > Add-Ins > Scripts > test_simple_gear.py > Run
```

For developers:
```bash
pytest tests/
```

## 📊 Performance

| Operation | Time | Components |
|-----------|------|------------|
| Generate HD (100T) | ~3s | 3 bodies |
| Export STL | ~2s | Per body |
| Full Assembly | ~8s | Complete |

## 🛠️ Development

See [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md) for detailed development roadmap.

### Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style
- Follow PEP 8
- Use type hints
- Document all functions
- Add unit tests

## 📚 Documentation

- [API Documentation](docs/API.md)
- [Tutorial](docs/TUTORIAL.md)
- [Theory & Math](docs/THEORY.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## 🔍 Known Issues

1. **Teeth are simplified** - Currently using trapezoidal approximation instead of true involute
2. **No mesh validation** - Gear engagement not verified
3. **Limited to spur gears** - Helical not supported (incompatible with HD)

## 📖 References

- [Fusion 360 API Documentation](https://help.autodesk.com/view/fusion360/ENU/?guid=GUID-A92A4B10-3781-4925-94C6-47DA85A4F65A)
- [SpurGear Sample](https://github.com/AutodeskFusion360/SpurGear)
- [Harmonic Drive Theory](https://www.harmonicdrive.net/technology)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Autodesk Fusion 360 team for the API
- SpurGear sample for involute profile reference
- Community contributors

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/HarmonicDriveGenerator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/HarmonicDriveGenerator/discussions)
- **Email**: your.email@example.com

---

**Note**: This is an active development project. Features and API may change.

**Current Version**: 0.1.0-alpha  
**Last Updated**: January 8, 2025  
**Fusion 360 Version**: 2.0.16490
