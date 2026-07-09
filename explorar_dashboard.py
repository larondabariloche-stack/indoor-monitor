#!/usr/bin/env python3
"""Explora el dashboard del admin"""
import sys, time, json
sys.path.insert(0, '/home/juan/.openclaw/workspace')
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    # Login
    page.goto("https://larondaclub.org/admin/login", wait_until="networkidle")
    time.sleep(1)
    page.fill('input[name="user"]', "alarijuan@gmail.com")
    page.fill('input[name="pass"]', "ElGr4nAlari")
    page.click('button.boton')
    time.sleep(3)
    
    print(f"📍 URL: {page.url}")
    
    # Tomar screenshot
    page.screenshot(path="/home/juan/.openclaw/workspace/admin_dashboard.png", full_page=True)
    
    # Explorar toda la interfaz - links navegación
    nav = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('a, button, [role="button"], .nav-link, .menu-item, li a')).map(el => ({
            tag: el.tagName,
            text: el.innerText.trim().substring(0, 80),
            href: el.href || '',
            class: el.className?.substring(0, 60) || ''
        })).filter(el => el.text);
    }""")
    
    print("\n🔗 Todos los elementos clickeables:")
    for e in nav:
        if e['text']:
            print(f"  [{e['text'][:60]}] class={e['class'][:40]}")
    
    # Texto completo de la página
    body = page.evaluate("() => document.body.innerText")
    print(f"\n📝 Texto completo:\n{body[:3000]}")
    
    # Ver inputs en la página actual
    inputs = page.evaluate("""() => {
        return Array.from(document.querySelectorAll('input, select, textarea')).map(el => ({
            tag: el.tagName,
            type: el.type || '',
            name: el.name || '',
            id: el.id || '',
            placeholder: el.placeholder || '',
            value: (el.value || '').substring(0, 40)
        }));
    }""")
    if inputs:
        print(f"\n📋 Inputs:")
        for i in inputs:
            print(f"  <{i['tag']} {i['name']} {i['type']} val='{i['value']}'>")
    
    browser.close()
