#!/usr/bin/env python3
"""
Helper para la Planilla de Cultivo.
Funciones para agregar registros de riego y manejar la planilla.
Uso: Python importable. Llamar desde watch_achu o manualmente.
"""

import json
import os
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = "1X6wGVPj4WtlNNnglBwqzE5VWPEPMuMrRD4z6mxqA7nY"
TOKEN_PATH = "/home/juan/.openclaw/workspace/token.json"


def get_sheets():
    with open(TOKEN_PATH) as f:
        tok = json.load(f)
    creds = Credentials.from_authorized_user_info(tok)
    if creds.expired:
        creds.refresh(Request())
    return build("sheets", "v4", credentials=creds)


def ultima_fila():
    """Devuelve el número de la primera fila vacía en Registro Cultivo."""
    sheets = get_sheets()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'Registro Cultivo'!A:A"
    ).execute()
    values = result.get("values", [])
    return len(values) + 1  # +1 porque la fila 1 es header


def agregar_riego(planta, fecha=None, agua_base="", ph_entrada="", ec_entrada="", notas=""):
    """
    Agrega un registro de riego al sheet 'Registro Cultivo'.
    
    Columnas: A=ID Planta | B=Fecha | C=Semana/Fase | D=Agua Base(EC)
              E=pH Entrada | F=EC Entrada | G=% Drenaje | H=pH Run-off
              I=EC Run-off | J=Temp/Humedad | K=Notas/Tareas
    """
    if not fecha:
        fecha = datetime.now().strftime("%d/%m/%Y")
    
    fila = ultima_fila()
    range_name = f"'Registro Cultivo'!A{ fila }:K{ fila }"
    
    body = {
        "values": [[
            planta,      # A: ID Planta
            fecha,       # B: Fecha
            "",          # C: Semana / Fase
            agua_base,   # D: Agua Base (EC)
            ph_entrada,  # E: pH Entrada
            ec_entrada,  # F: EC Entrada
            "",          # G: % Drenaje
            "",          # H: pH Run-off
            "",          # I: EC Run-off
            "",          # J: Temp/Humedad
            notas        # K: Notas / Tareas
        ]]
    }
    
    sheets = get_sheets()
    result = sheets.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    return fila


def listar_geneticas():
    """Devuelve lista de genéticas únicas del inventario."""
    sheets = get_sheets()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'🌱 Inventario de Plantas'!B:B"
    ).execute()
    values = result.get("values", [])
    geneticas = set()
    for row in values[1:]:  # saltar header
        if row and row[0].strip():
            geneticas.add(row[0].strip())
    return sorted(geneticas)


def buscar_planta(genetica_o_id):
    """Busca plantas por genética o ID. Devuelve lista de IDs."""
    sheets = get_sheets()
    result = sheets.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range="'🌱 Inventario de Plantas'!A:G"
    ).execute()
    values = result.get("values", [])
    
    resultados = []
    for row in values[1:]:
        if len(row) >= 2:
            pid = row[0].strip()
            genetica = row[1].strip()
            if genetica_o_id.lower() in genetica.lower() or genetica_o_id == pid:
                resultados.append({
                    "id": pid,
                    "genetica": genetica,
                    "tipo": row[2] if len(row) > 2 else "",
                    "fase": row[5] if len(row) > 5 else "",
                    "ubicacion": row[4] if len(row) > 4 else ""
                })
    return resultados


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "listar":
        print("Genéticas disponibles:", ", ".join(listar_geneticas()))
    elif len(sys.argv) > 2 and sys.argv[1] == "buscar":
        for p in buscar_planta(sys.argv[2]):
            print(f"  ID {p['id']}: {p['genetica']} ({p['fase']})")
    else:
        print("Uso:")
        print("  python3 planilla_cultivo.py listar")
        print("  python3 planilla_cultivo.py buscar <genetica>")
