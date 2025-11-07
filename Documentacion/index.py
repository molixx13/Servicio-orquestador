#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
portal_documentaciones.py
-------------------------
Portal central para acceder a los servidores de documentación de cada servicio.

Cada microservicio de documentación (Tienda, Compras/Ventas, etc.)
ya expone su propia interfaz HTTP con IP y puerto configurado.

Este portal simplemente detecta si están activos y abre el navegador hacia ellos.

Autor: Molixx13
Versión: 2.0 (Modo Oscuro)
"""

import tkinter as tk
from tkinter import messagebox
import webbrowser
import socket
import threading
import time

# ---------------------------------------------------------------------
# CONFIGURACIÓN DE SERVICIOS
# ---------------------------------------------------------------------

SERVICIOS = [
    {
        "nombre": "Contabilidad",
        "ip": "192.168.100.233",
        "puerto": 8090,
        "descripcion": "Genera facturas e informes contables automáticos."
    },
    {
        "nombre": "Inventario",
        "ip": "192.168.100.233",
        "puerto": 8091,
        "descripcion": "Gestión del stock de productos y control de existencias."
    },
    {
        "nombre": "Proveedores",
        "ip": "192.168.100.233",
        "puerto": 8092,
        "descripcion": "Administra pedidos de reabastecimiento automático."
    },
    {
        "nombre": "Compras/Ventas",
        "ip": "192.168.100.233",
        "puerto": 8093,
        "descripcion": "Registra todas las transacciones comerciales del sistema."
    },
    {
        "nombre": "Tienda",
        "ip": "192.168.100.233",
        "puerto": 8094,
        "descripcion": "Interfaz de cliente que muestra el catálogo y recibe facturas."
    },
    {
        "nombre": "Transportadora",
        "ip": "192.168.100.233",
        "puerto": 8095,
        "descripcion": "Gestión del transporte y envío de pedidos generados."
    }
]

# ---------------------------------------------------------------------
# FUNCIONES AUXILIARES
# ---------------------------------------------------------------------

def verificar_servidor(ip, puerto, timeout=0.5):
    """Verifica si el servidor de documentación está activo."""
    try:
        with socket.create_connection((ip, puerto), timeout=timeout):
            return True
    except Exception:
        return False

def abrir_documentacion(ip, puerto):
    """Abre la documentación correspondiente en el navegador."""
    url = f"http://{ip}:{puerto}"
    webbrowser.open_new_tab(url)

# ---------------------------------------------------------------------
# INTERFAZ TKINTER (modo oscuro)
# ---------------------------------------------------------------------

class PortalDocumentaciones:
    def __init__(self, root):
        self.root = root
        self.root.title("📘 Portal de Documentaciones — Sistema Distribuido")
        self.root.geometry("900x560")
        self.root.configure(bg="#0f1117")

        # encabezado
        header = tk.Frame(root, bg="#0f1117")
        header.pack(fill="x", padx=20, pady=(20,10))

        tk.Label(
            header, text="📚 Centro de Documentación de Servicios",
            font=("Segoe UI", 18, "bold"), fg="#e6eef8", bg="#0f1117"
        ).pack(anchor="w")

        tk.Label(
            header,
            text="Selecciona un servicio para abrir su documentación técnica (Python).",
            font=("Segoe UI", 10), fg="#9aa4b2", bg="#0f1117"
        ).pack(anchor="w", pady=(6, 0))

        # contenedor principal
        self.container = tk.Frame(root, bg="#0f1117")
        self.container.pack(fill="both", expand=True, padx=20, pady=(10,20))

        # crear tarjetas para cada servicio
        self.cards = []
        self._crear_tarjetas()

        # hilo para actualizar estados
        self._actualizar_estados_en_hilo()

    def _crear_tarjetas(self):
        cols = 2
        r, c = 0, 0

        for servicio in SERVICIOS:
            frame = tk.Frame(self.container, bg="#111216", bd=0, relief="flat", padx=16, pady=16)
            frame.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
            self.container.grid_columnconfigure(c, weight=1)

            # título
            tk.Label(
                frame, text=f"🧩 {servicio['nombre']}",
                font=("Segoe UI", 13, "bold"), fg="#cfe6ff", bg="#111216"
            ).pack(anchor="w")

            # descripción
            tk.Label(
                frame, text=servicio["descripcion"],
                font=("Segoe UI", 9), fg="#9aa4b2", bg="#111216", wraplength=380, justify="left"
            ).pack(anchor="w", pady=(6,10))

            # IP y puerto
            tk.Label(
                frame,
                text=f"📍 IP: {servicio['ip']}     🔌 Puerto: {servicio['puerto']}",
                font=("Segoe UI", 9), fg="#85909a", bg="#111216"
            ).pack(anchor="w")

            # estado (se actualizará dinámicamente)
            estado_lbl = tk.Label(
                frame, text="🔴 Inactivo", font=("Segoe UI", 10, "bold"),
                fg="#ef4444", bg="#111216"
            )
            estado_lbl.pack(anchor="w", pady=(8,4))

            # botón abrir
            btn = tk.Button(
                frame, text="🌐 Abrir Documentación", bg="#374151", fg="#e6eef8",
                font=("Segoe UI", 10, "bold"), bd=0, padx=10, pady=6,
                activebackground="#4b5563",
                command=lambda ip=servicio["ip"], p=servicio["puerto"]: abrir_documentacion(ip, p)
            )
            btn.pack(anchor="e", pady=(6,0))

            self.cards.append({
                "servicio": servicio,
                "estado_lbl": estado_lbl
            })

            c += 1
            if c >= cols:
                c = 0
                r += 1

    def _actualizar_estados_en_hilo(self):
        """Hilo que actualiza cada 3 segundos el estado (activo/inactivo)."""
        def actualizar():
            while True:
                for card in self.cards:
                    s = card["servicio"]
                    activo = verificar_servidor(s["ip"], s["puerto"])
                    lbl = card["estado_lbl"]
                    if activo:
                        lbl.config(text="🟢 Activo", fg="#22c55e")
                    else:
                        lbl.config(text="🔴 Inactivo", fg="#ef4444")
                time.sleep(3)

        hilo = threading.Thread(target=actualizar, daemon=True)
        hilo.start()

# ---------------------------------------------------------------------
# EJECUCIÓN PRINCIPAL
# ---------------------------------------------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = PortalDocumentaciones(root)
    root.mainloop()
