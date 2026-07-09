#!/usr/bin/env python3
"""
Genera un dashboard HTML visual del indoor desde la Planilla de Cultivo.
Auto-refresh cada 5 min + timeline visual de flora.
"""
import json
from datetime import datetime, timezone, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1X6wGVPj4WtlNNnglBwqzE5VWPEPMuMrRD4z6mxqA7nY"
TOKEN_PATH = "/home/juan/.openclaw/workspace/token.json"
OUTPUT_PATH = "/home/juan/Escritorio/dashboard_indoor.html"

# Config
FLORA_START = datetime(2026, 6, 9)  # Inicio flora 09/06
FLORA_DURATION = 70  # Días de flora (10 semanas)
FLORA_WEEKS = 10

COLORES_FASE = ['#8B5CF6', '#3B82F6', '#EF4444', '#F59E0B', '#10B981', '#EC4899', '#6B7280']

def get_sheets():
    with open(TOKEN_PATH) as f:
        data = json.load(f)
    creds = Credentials.from_authorized_user_info(data)
    return build("sheets", "v4", credentials=creds)

def get_range(sheet_name, range_str):
    sheets = get_sheets()
    return sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"'{sheet_name}'!{range_str}"
    ).execute().get("values", [])

def parse_date(datestr):
    """Intenta parsear fecha en formato DD/MM o DD/MM/YYYY."""
    if not datestr:
        return None
    datestr = datestr.strip()
    for fmt in ("%d/%m/%Y", "%d/%m/%y", "%d/%m"):
        try:
            if fmt == "%d/%m":
                return datetime.strptime(datestr + "/2026", "%d/%m/%Y")
            return datetime.strptime(datestr, fmt)
        except ValueError:
            continue
    return None

def calcular_semana_flora(dia_flora):
    """Calcula semana de flora (1-indexed) dado el día."""
    return min((dia_flora // 7) + 1, FLORA_WEEKS)

def build_html():
    now_ar = datetime.now(timezone(timedelta(hours=-3)))
    now_str = now_ar.strftime("%d/%m/%Y %H:%M")

    # ─── Datos ──────────────────────────────────
    inventario = get_range("🌱 Inventario de Plantas", "A:G")
    registros = get_range("Registro Cultivo", "A:K")

    plantas = []
    for row in inventario[1:]:
        if len(row) >= 6 and row[0].strip():
            plantas.append({
                'id': row[0].strip(),
                'genetica': row[1].strip() if len(row) > 1 else '',
                'tipo': row[2].strip() if len(row) > 2 else '',
                'fecha': row[3].strip() if len(row) > 3 else '',
                'ubicacion': row[4].strip() if len(row) > 4 else '',
                'fase': row[5].strip() if len(row) > 5 else '',
                'notas': row[6].strip() if len(row) > 6 else ''
            })

    total = len(plantas)
    por_fase = {}
    por_genetica = {}
    por_tipo = {}
    for p in plantas:
        por_fase[p['fase'] or 'Sin fase'] = por_fase.get(p['fase'] or 'Sin fase', 0) + 1
        por_genetica[p['genetica'] or 'Sin ID'] = por_genetica.get(p['genetica'] or 'Sin ID', 0) + 1
        por_tipo[p['tipo'] or 'Sin tipo'] = por_tipo.get(p['tipo'] or 'Sin tipo', 0) + 1

    # Últimos riegos
    ultimos_riegos = []
    for row in reversed(registros[1:]):
        if len(row) >= 7 and row[0].strip() and row[0].strip() not in ['📋 PLAN ALIMENTACIÓN', '📋 CORRECCIÓN PLAN']:
            ultimos_riegos.append({
                'planta': row[0].strip(), 'fecha': row[1].strip() if len(row) > 1 else '',
                'ec': row[5].strip() if len(row) > 5 else '',
                'ph': row[4].strip() if len(row) > 4 else '',
                'volumen': row[3].strip() if len(row) > 3 else '',
                'notas': row[10].strip() if len(row) > 10 else ''
            })
            if len(ultimos_riegos) >= 8:
                break

    sin_ubicacion = [p for p in plantas if not p['ubicacion']]
    sin_fase = [p for p in plantas if p['fase'] in ['', 'Sin fase']]
    now_naive = now_ar.replace(tzinfo=None)
    germ_plants = [p for p in plantas if p['fase'] == 'Germinación' and p['fecha']]
    germ_viejos = [p for p in germ_plants if parse_date(p['fecha']) and (now_naive - parse_date(p['fecha'])).days > 21]

    # ─── Timeline Flora ─────────────────────────
    flora_delta = (now_naive - FLORA_START).days
    dia_flora = max(1, flora_delta + 1)  # Day 1 = June 9
    semana_flora = calcular_semana_flora(dia_flora)
    progreso_pct = min(100, round((dia_flora / FLORA_DURATION) * 100))
    dias_restantes = max(0, FLORA_DURATION - dia_flora)

    cosecha_est = FLORA_START + timedelta(days=FLORA_DURATION)
    cosecha_str = cosecha_est.strftime("%d/%m")

    # ─── Armado HTML ────────────────────────────
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="300">
<title>🌿 Dashboard Indoor - La Ronda</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:'Inter',sans-serif; background:#0f0f0f; color:#e0e0e0; padding:20px; }}
.header {{ display:flex; justify-content:space-between; align-items:center; margin-bottom:28px; padding-bottom:16px; border-bottom:1px solid #2a2a2a; }}
.header h1 {{ font-size:26px; font-weight:800; background:linear-gradient(135deg,#4ade80,#22c55e); -webkit-background-clip:text; -webkit-text-fill-color:transparent; }}
.header span {{ font-size:14px; color:#888; }}
.badge {{ display:inline-block; font-size:11px; padding:3px 8px; border-radius:10px; margin-left:6px; }}
.badge-green {{ background:#166534; color:#4ade80; }}
.badge-auto {{ background:#831843; color:#f472b6; }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:20px; margin-bottom:24px; }}
.card {{ background:#1a1a1a; border-radius:16px; padding:20px; border:1px solid #2a2a2a; }}
.card h2 {{ font-size:15px; font-weight:600; color:#9ca3af; text-transform:uppercase; letter-spacing:.5px; margin-bottom:12px; }}
.numero {{ font-size:42px; font-weight:800; color:#4ade80; line-height:1; }}
.numero small {{ font-size:16px; font-weight:400; color:#888; }}
.bar-container {{ display:flex; gap:6px; align-items:center; margin:4px 0; }}
.bar-label {{ width:110px; font-size:13px; color:#ccc; text-align:right; }}
.bar {{ flex:1; height:22px; border-radius:6px; background:#2a2a2a; }}
.bar-fill {{ height:100%; border-radius:6px; display:flex; align-items:center; justify-content:flex-end; padding-right:6px; font-size:11px; font-weight:600; color:#fff; min-width:30px; }}

/* ── Timeline Flora ── */
.timeline {{ margin-top:16px; }}
.timeline-bar {{ position:relative; height:32px; background:#2a2a2a; border-radius:16px; overflow:hidden; }}
.timeline-progress {{ height:100%; background:linear-gradient(90deg,#4ade80,#22c55e,#16a34a); border-radius:16px; transition:width .5s; display:flex; align-items:center; justify-content:flex-end; padding-right:10px; font-size:12px; font-weight:700; color:#000; min-width:40px; }}
.timeline-weeks {{ display:flex; justify-content:space-between; margin-top:4px; font-size:11px; color:#555; padding:0 4px; }}
.timeline-weeks span {{ position:relative; }}
.timeline-weeks span.week-active {{ color:#4ade80; font-weight:700; }}
.timeline-info {{ display:flex; justify-content:space-between; margin-top:8px; font-size:13px; }}
.timeline-info div {{ text-align:center; }}
.timeline-info .label {{ color:#888; font-size:11px; }}
.timeline-info .value {{ color:#e0e0e0; font-size:18px; font-weight:700; }}
.timeline-info .value.highlight {{ color:#4ade80; }}

.rooms {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; }}
.room {{ background:#1a1a1a; border-radius:16px; padding:20px; border:1px solid #2a2a2a; }}
.room h2 {{ font-size:18px; font-weight:700; margin-bottom:12px; }}
.room h3 {{ font-size:13px; font-weight:600; margin-bottom:6px; margin-top:14px; }}
.room.flora {{ border-color:#ef444433; }} .room.flora h2 {{ color:#ef4444; }}
.room.vege {{ border-color:#3b82f633; }} .room.vege h2 {{ color:#3b82f6; }}
.room ul {{ list-style:none; }}
.room li {{ padding:6px 0; border-bottom:1px solid #222; font-size:13px; display:flex; justify-content:space-between; }}
.room li:last-child {{ border:none; }}
.riego-item {{ padding:8px 0; border-bottom:1px solid #222; font-size:13px; }}
.riego-item:last-child {{ border:none; }}
.riego-fecha {{ color:#888; font-size:11px; }}
.riego-ec {{ color:#4ade80; font-weight:600; }}
.riego-ph {{ color:#60a5fa; }}
.alert {{ background:#f59e0b11; border-left:3px solid #f59e0b; padding:8px 12px; border-radius:6px; margin:4px 0; font-size:13px; color:#fbbf24; }}
.alert-danger {{ background:#ef444411; border-left:3px solid #ef4444; color:#f87171; }}
.alert-success {{ background:#4ade8011; border-left:3px solid #4ade80; color:#4ade80; }}
.alert-info {{ background:#3b82f611; border-left:3px solid #3b82f6; color:#60a5fa; }}
.footer {{ text-align:center; margin-top:24px; font-size:12px; color:#555; border-top:1px solid #222; padding-top:16px; }}
.footer .refresh-note {{ color:#444; font-size:11px; }}
</style>
</head>
<body>
<div class="header">
    <h1>🌿 Dashboard Indoor · La Ronda</h1>
    <div style="text-align:right;"><span>{now_str}</span><br><span class="badge badge-green" style="margin-left:0;">⏱️ auto-refresh 5 min</span></div>
</div>

<div class="grid">
    <div class="card"><h2>🌱 Total Plantas</h2><div class="numero">{total}</div></div>
    <div class="card"><h2>🧬 Genéticas</h2><div class="numero">{len(por_genetica)} <small>distintas</small></div></div>
    <div class="card"><h2>📊 Por Tipo</h2>"""
    for tipo, count in sorted(por_tipo.items(), key=lambda x: -x[1]):
        html += f'<div class="bar-container"><div class="bar-label">{tipo}</div><div class="bar"><div class="bar-fill" style="width:{max(15,count/total*100)}%;background:#4ade80">{count}</div></div></div>'
    html += """</div>
    <div class="card"><h2>🌱 Por Fase</h2>"""
    for i, (fase, count) in enumerate(sorted(por_fase.items(), key=lambda x: -x[1])):
        c = COLORES_FASE[i % len(COLORES_FASE)]
        html += f'<div class="bar-container"><div class="bar-label">{fase}</div><div class="bar"><div class="bar-fill" style="width:{max(15,count/total*100)}%;background:{c}">{count}</div></div></div>'
    html += """</div>
</div>

<!-- ════ FLORA TIMELINE ════ -->
<div class="card" style="margin-bottom:24px;">
    <h2>🔥 Flora — Timeline</h2>
    <div class="timeline">
        <div class="timeline-bar">
            <div class="timeline-progress" style="width:""" + str(progreso_pct) + """%;">S""" + str(semana_flora) + """</div>
        </div>
        <div class="timeline-weeks">"""
    for w in range(1, FLORA_WEEKS + 1):
        cls = "week-active" if w == semana_flora else ""
        html += f'<span class="{cls}">{"🌱" if w <= 2 else "🌿" if w <= 6 else "🍅"} S{w}</span>'
    html += f"""</div>
        <div class="timeline-info">
            <div><span class="label">Día</span><br><span class="value">{dia_flora}</span></div>
            <div><span class="label">Semana</span><br><span class="value highlight">{semana_flora} / {FLORA_WEEKS}</span></div>
            <div><span class="label">Progreso</span><br><span class="value highlight">{progreso_pct}%</span></div>
            <div><span class="label">Restan</span><br><span class="value">{dias_restantes} días</span></div>
            <div><span class="label">Cosecha est.</span><br><span class="value">{cosecha_str}</span></div>
        </div>
    </div>
</div>

<!-- ════ SALAS ════ -->
<h2 style="margin-bottom:14px;font-size:18px;">🏠 Salas</h2>
<div class="rooms">
"""
    # ── FLORA ──
    flora = [p for p in plantas if p['fase'] == 'Flora' or 'flora' in p['ubicacion'].lower()]
    html += f'<div class="room flora"><h2>🔥 Sala de Flora · Día {dia_flora}</h2>'
    html += f'<p style="font-size:12px;color:#666;margin-top:-6px;margin-bottom:10px;">🌱 Inicio {FLORA_START.strftime("%d/%m")} · 🍅 Cosecha est. {cosecha_str}</p>'
    if flora:
        # Agrupar por genética
        gc = {}
        for p in flora:
            gc[p['genetica']] = gc.get(p['genetica'], 0) + 1
        for g, c in sorted(gc.items(), key=lambda x: -x[1]):
            html += f'<li><span>{g}</span><span>{c}</span></li>'
        html += '</ul>'
        html += f'<p style="margin-top:8px;font-size:13px;color:#666;">Total: <strong style="color:#ccc;">{len(flora)}</strong></p>'
    html += '<div style="margin-top:12px;padding-top:10px;border-top:1px solid #222;"><p style="font-size:13px;color:#888;">📝 Último riego:</p><p style="font-size:13px;color:#ccc;">06/07 — 100L · AB:5 / C:3.5 · EC 1.9</p></div></div>'

    # ── VEGE ──
    vege = [p for p in plantas if 'catamarca' in p['ubicacion'].lower()]
    vgerm = [p for p in vege if p['fase'] == 'Germinación']
    vveg = [p for p in vege if p['fase'] in ('Vegetativo', 'Crecimiento')]
    vauto = [p for p in vege if p['tipo'] == 'Autofloreciente']
    html += '<div class="room vege"><h2>🌿 Sala Vege · Catamarca</h2>'
    if vgerm:
        html += f'<h3 style="color:#8B5CF6;">🌱 Germinación ({len(vgerm)})</h3><ul>'
        gc = {}
        for p in vgerm:
            gc[p['genetica']] = gc.get(p['genetica'], 0) + 1
        for g, c in sorted(gc.items(), key=lambda x: -x[1], reverse=True):
            html += f'<li><span>{g}</span><span>{c}</span></li>'
        html += '</ul>'
    if vauto:
        html += f'<h3 style="color:#EC4899;">⚡ Autoflorecientes ({len(vauto)})</h3><ul>'
        gc = {}
        for p in vauto:
            gc[p['genetica']] = gc.get(p['genetica'], 0) + 1
        for g, c in sorted(gc.items(), key=lambda x: -x[1], reverse=True):
            html += f'<li><span>{g}</span><span>{c} · desde 25/05</span></li>'
        html += '</ul>'
    if vveg:
        no_auto = [p for p in vveg if p['tipo'] != 'Autofloreciente']
        if no_auto:
            html += f'<h3 style="color:#3B82F6;">🌿 Vegetativo ({len(no_auto)})</h3><ul>'
            gc = {}
            for p in no_auto:
                gc[p['genetica']] = gc.get(p['genetica'], 0) + 1
            for g, c in sorted(gc.items(), key=lambda x: -x[1], reverse=True):
                html += f'<li><span>{g}</span><span>{c}</span></li>'
            html += '</ul>'
    html += f'<p style="margin-top:14px;padding-top:10px;border-top:1px solid #222;font-size:13px;color:#666;">Total: <strong style="color:#ccc;">{len(vege)}</strong></p></div></div>'

    # ════ BOTTOM: Alertas + Riegos ════
    html += '<div class="grid" style="margin-top:20px;"><div class="card"><h2>⚠️ Alertas</h2>'
    alertas = []
    if sin_ubicacion:
        alertas.append((f"⚠️ {len(sin_ubicacion)} plantas sin ubicación asignada", "alert"))
    if sin_fase:
        alertas.append((f"⚠️ {len(sin_fase)} plantas sin fase actual", "alert"))
    if germ_viejos:
        alertas.append((f"🔴 {len(germ_viejos)} en Germinación hace >21 días — revisar", "alert-danger"))
    if dia_flora >= 28 and dia_flora <= 35:
        alertas.append(("💡 Semana 4-5 de flora — cambiar a nutrientes de engorde si no lo hiciste", "alert-info"))
    if dia_flora >= 56:
        alertas.append(("💡 Últimas 2 semanas de flora — preparar lavado de raíces", "alert-info"))
    if not alertas:
        alertas.append(("✅ Todo en orden", "alert-success"))
    for texto, tipo in alertas:
        html += f'<div class="{tipo}">{texto}</div>'

    html += '</div><div class="card"><h2>📋 Últimos riegos</h2>'
    for r in ultimos_riegos:
        ec_html = f' · EC <span class="riego-ec">{r["ec"]}</span>' if r['ec'] else ''
        ph_html = f' · pH <span class="riego-ph">{r["ph"]}</span>' if r['ph'] else ''
        vol_html = f' · {r["volumen"]}L' if r['volumen'] else ''
        html += f'<div class="riego-item"><span class="riego-fecha">{r["fecha"]}</span> — <strong>{r["planta"]}</strong>{vol_html}{ec_html}{ph_html}<br><span style="color:#888;font-size:12px;">{r["notas"]}</span></div>'
    if not ultimos_riegos:
        html += '<p style="color:#666;font-size:13px;">Sin datos de riego aún</p>'
    html += '</div></div>'

    html += f'<div class="footer">🌙 Dashboard · La Ronda · Auto-refresh cada 5 min<br><span class="refresh-note">Última actualización: {now_str}</span></div></body></html>'

    return html

if __name__ == "__main__":
    try:
        html = build_html()
        with open(OUTPUT_PATH, 'w') as f:
            f.write(html)
        print(f"✅ Dashboard generado → {OUTPUT_PATH}")
    except Exception as e:
        print(f"❌ Error: {e}")
