# 🌿 Indoor Monitor - La Ronda ONG

Dashboard de monitoreo de cultivo indoor para La Ronda ONG (cannabis medicinal).

## 🚀 Quick Start

```bash
# Instalar dependencias
pip install openpyxl

# Generar el dashboard HTML
python3 generar_dashboard.py

# Abrir laronda_dashboard.html en el navegador
```

## 📁 Archivos

- `generar_dashboard.py` — Script principal que genera el dashboard visual
- `laronda_dashboard.html` — Dashboard HTML auto-refrescable
- `planilla_cultivo.py` — Gestión de planilla de cultivo
- `planilla_cultivo.xlsx` — Datos del cultivo
- `calendar_deadlines_indoor.py` — Fechas clave del indoor
- `indoor/fotos/` — Fotos del indoor
- `indoor_logs/riego.md` — Bitácora de riego

## 🔄 Auto-refresh

El dashboard HTML se refresca automáticamente cada 5 minutos.
