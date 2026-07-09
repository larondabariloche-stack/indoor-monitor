#!/usr/bin/env python3
"""
Genera deadlines en Google Calendar para implementación del indoor
Fecha objetivo: 15 de mayo de 2026
"""

import os
import sys
from datetime import datetime, timedelta

# Agregar path para imports
sys.path.insert(0, '/home/juan/.openclaw/workspace')

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

SCOPES = ['https://www.googleapis.com/auth/calendar']
TOKEN_PATH = '/home/juan/.openclaw/workspace/token.json'

# Tareas con deadlines (trabajando hacia el 15/05)
# Format: (titulo, descripcion, fecha_inicio, fecha_fin, color)
tareas = [
    # SEMANA 1: Infraestructura base (5-10 mayo)
    {
        'titulo': '📅 DEADLINE: Comprar e instalar aire acondicionado',
        'desc': 'Sala de cultivo - Calle Catamarca. Instalar split o sistema de climatización.',
        'inicio': '2026-05-07T10:00:00',
        'fin': '2026-05-07T12:00:00',
        'color': '11',  # Rojo
    },
    {
        'titulo': '📅 DEADLINE: Instalar luces LED',
        'desc': 'Montar sistema de iluminación para sala de cultivo indoor.',
        'inicio': '2026-05-08T10:00:00',
        'fin': '2026-05-08T12:00:00',
        'color': '11',
    },
    {
        'titulo': '📅 DEADLINE: Armar camas / estructura',
        'desc': 'Construir o montar las camas/cajones para las plantas. Herramientas disponibles.',
        'inicio': '2026-05-09T10:00:00',
        'fin': '2026-05-09T14:00:00',
        'color': '11',
    },
    
    # SEMANA 2: Sistemas y control (11-13 mayo)
    {
        'titulo': '📅 DEADLINE: Sistema de ventilación (intracción/extracción)',
        'desc': 'Instalar extractor e intracción pasiva. Presión negativa para control de olores.',
        'inicio': '2026-05-12T10:00:00',
        'fin': '2026-05-12T14:00:00',
        'color': '11',
    },
    {
        'titulo': '📅 DEADLINE: Control de agua (pH + EC)',
        'desc': 'Comprar medidor de pH y EC. Definir sistema de riego (autopots/detelas).',
        'inicio': '2026-05-13T10:00:00',
        'fin': '2026-05-13T12:00:00',
        'color': '11',
    },
    {
        'titulo': '📅 DEADLINE: Macetas y sustrato',
        'desc': 'Comprar macetas (autopots/detelas), sustrato, fertilizantes.',
        'inicio': '2026-05-13T14:00:00',
        'fin': '2026-05-13T16:00:00',
        'color': '11',
    },
    
    # SEMANA FINAL: Trazabilidad y plantas (14-15 mayo)
    {
        'titulo': '📅 DEADLINE: Etiquetas y sistema de trazabilidad',
        'desc': 'Crear etiquetas con códigos de barras para cada planta. Cuadro de control.',
        'inicio': '2026-05-14T10:00:00',
        'fin': '2026-05-14T12:00:00',
        'color': '11',
    },
    {
        'titulo': '🎯 DÍA D: Implementación indoor - Todo listo',
        'desc': 'Sala de cultivo operativa en Calle Catamarca. Plantas vegetando.',
        'inicio': '2026-05-15T08:00:00',
        'fin': '2026-05-15T20:00:00',
        'color': '9',  # Verde (color especial para el día D)
    },
    
    # TAREA ADICIONAL: Documentación
    {
        'titulo': '📋 Revisar cartas documento (Ministerio + Municipalidad)',
        'desc': 'Verificar estado de fiscalización Sedronar y documentación REPROCANN.',
        'inicio': '2026-05-10T10:00:00',
        'fin': '2026-05-10T11:00:00',
        'color': '5',  # Amarillo
    },
]

def main():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("Error: Token no válido. Autenticar primero.")
            sys.exit(1)
    
    service = build('calendar', 'v3', credentials=creds)
    
    # Obtener calendario principal
    calendar_id = 'primary'
    
    creados = 0
    for tarea in tareas:
        evento = {
            'summary': tarea['titulo'],
            'description': tarea['desc'],
            'start': {
                'dateTime': tarea['inicio'],
                'timeZone': 'America/Argentina/Salta',
            },
            'end': {
                'dateTime': tarea['fin'],
                'timeZone': 'America/Argentina/Salta',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 1440},  # 1 día antes
                    {'method': 'popup', 'minutes': 60},    # 1 hora antes
                ],
            },
            'colorId': tarea['color'],
        }
        
        try:
            event = service.events().insert(calendarId=calendar_id, body=evento).execute()
            print(f"✅ Creado: {tarea['titulo']}")
            print(f"   📅 {tarea['inicio']} → {event.get('htmlLink')}")
            creados += 1
        except Exception as e:
            print(f"❌ Error creando '{tarea['titulo']}': {e}")
    
    print(f"\n🎯 Total eventos creados: {creados}/{len(tareas)}")

if __name__ == '__main__':
    main()
