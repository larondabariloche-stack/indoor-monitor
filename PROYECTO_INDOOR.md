# 🌱 Proyecto Indoor - Gestión de Cultivo con QR

## Estado: 🟡 EN PROCESO

## Qué se hizo
- **19/05/2026:** Juan inició el proyecto. Se creó planilla de cultivo en Drive y se planteó sistema de seguimiento por QR.

## Estructura en Drive
- **Carpeta:** 🌿 La Ronda - Organización > 04_PROYECTOS > Indoor > Sala de Veg
- **Planilla:** [🌱 Planilla de Cultivo](https://docs.google.com/spreadsheets/d/1X6wGVPj4WtlNNnglBwqzE5VWPEPMuMrRD4z6mxqA7nY/edit)
  - Columnas: Fecha, Semana/Fase, Agua Base (EC), pH Entrada, EC Entrada, % Drenaje, pH Run-off, EC Run-off, Temp/Humedad, Notas/Tareas
- **Fotos del indoor:** `indoor/fotos/` (locales) y en Drive > Sala de Veg
- **Foto impresora:** `indoor/fotos/impresora.jpg` (guardada, pendiente de identificar modelo)

## Sub-agente cultivador
- **Brief creado:** `memory/BRIEF_CULTIVADOR.md`
- Funciona similar al contador: se spawnea con `sessions_spawn` cuando se necesita cargar datos o analizar el cultivo
- Sabe interpretar pH run-off, EC run-off, % drenaje, y dar recomendaciones

## Sistema QR (planificado, no implementado)
### Idea general
1. Cada maceta tiene un **código QR** con un ID único (ej: `INDOOR-001`)
2. El QR linkea a un **Google Form** con el ID precargado
3. Escaneás → completás datos (pH, EC, temp, notas) → se guarda automático en la planilla
4. Después se puede ver historial por planta

### Qué se hizo
- **19/05/2026:** Juan inició el proyecto. Se creó planilla de cultivo en Drive y se planteó sistema de seguimiento por QR.
- **20/05/2026:** Reestructura completa de la planilla:
  - ✅ Columna **ID Planta** agregada al registro diario
  - ✅ Pestaña **🌱 Inventario de Plantas** creada con 30 esquejes Tropicanna (TR-001 a TR-030)
  - ✅ Sistema de IDs definido: TR-XXX para Tropicanna, SD-XXX para semilla
  - Pendiente: cargar semillas cuando Juan defina cuántas

## Pendiente
- [ ] Identificar modelo de impresora
- [ ] Cargar semillas en inventario (pendiente definición)
- [ ] Asignar ubicaciones en el indoor a las plantas
- [ ] Crear Google Form vinculado
- [ ] Generar QR codes
- [ ] Testear impresión de etiquetas 15x30mm
- [ ] Implementar escaneo
