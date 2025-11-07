#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
doc_portal_pydoc.py
-------------------
Portal local (Tkinter) que arranca un servidor pydoc y abre
la documentación de módulos Python en el navegador.

Características:
- Usa un solo servidor pydoc HTTP (puerto configurable, por defecto 8085).
- Interfaz Tkinter (modo oscuro) con botones para cada módulo/documentación.
- Botón para detener el servidor pydoc desde la UI.
- Requiere que los módulos .py sean importables (estén en la misma carpeta o en PYTHONPATH).

Ejecutar:
    python doc_portal_pydoc.py

Nota:
- Si tus archivos de documentación son scripts Python (pydoc-style),
  asegúrate de que sus nombres de módulo (sin .py) coincidan con las claves
  en MODULE_MAP o añade su carpeta al sys.path.
"""
import os
import sys
import subprocess
import time
import webbrowser
import signal
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

# -------------------------
# CONFIGURACIÓN
# -------------------------
# Puerto donde correrá pydoc HTTP
PYDOC_PORT = 8085

# Mapa: etiqueta visible -> módulo_name (importable module name, sin .py)
# Asegúrate de que los .py estén en la misma carpeta que este script o en PYTHONPATH.
MODULE_MAP = {
    "Contabilidad": "documentacionContabilidad",
    "Inventario": "documentacionInventario",
    "Proveedores": "documentacionProvedores",
    "Compras/Ventas": "documentacionCompras",
    "Tienda": "documentacionTienda",
    "Transportadora": "documentacionTransportadora",
}

# Tiempo que espera a que el servidor pydoc esté listo (s)
STARTUP_WAIT = 0.6

# -------------------------
# UTILIDADES
# -------------------------

def ensure_cwd_in_path():
    """Poner la carpeta actual (donde está el portal) en sys.path para que pydoc importe módulos locales."""
    cwd = str(Path.cwd())
    if cwd not in sys.path:
        sys.path.insert(0, cwd)

def start_pydoc_server(port=PYDOC_PORT):
    """
    Inicia un servidor pydoc en background con subprocess.
    Devuelve el Popen object.
    Usa: python -m pydoc -p <port>
    """
    ensure_cwd_in_path()
    python = sys.executable
    cmd = [python, "-m", "pydoc", "-p", str(port)]
    # On Windows, DETACHED_PROCESS prevents console window pop-up; keep it simple and portable.
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return proc

def stop_process(proc):
    """Detener proceso (pydoc) de forma segura."""
    if proc is None:
        return
    try:
        # try terminate gracefully
        proc.terminate()
        proc.wait(timeout=2)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass

def open_module_doc(module_name, host="localhost", port=PYDOC_PORT):
    """
    Abre en el navegador la página pydoc del módulo.
    pydoc HTTP server expone /module_name
    """
    url = f"http://{host}:{port}/{module_name}"
    webbrowser.open_new_tab(url)

# -------------------------
# INTERFAZ TK (modo oscuro)
# -------------------------

class DocPortalApp:
    def __init__(self, master, module_map, pydoc_port=PYDOC_PORT):
        self.master = master
        self.module_map = module_map
        self.pydoc_port = pydoc_port
        self.pydoc_proc = None

        master.title("📘 Portal Pydoc - Documentación (Modo Oscuro)")
        master.geometry("820x520")
        master.configure(bg="#0f1117")
        # no resize small
        master.minsize(720, 440)

        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self.master, bg="#0f1117")
        header.pack(fill="x", padx=18, pady=(18, 6))

        title = tk.Label(header, text="📘 Centro de Documentación (pydoc)", fg="#e6eef8",
                         bg="#0f1117", font=("Segoe UI", 18, "bold"))
        title.pack(anchor="w")

        subtitle = tk.Label(header, text=f"Servidor pydoc local -> http://localhost:{self.pydoc_port}/  —  Módulos importables en la carpeta actual",
                            fg="#9aa4b2", bg="#0f1117", font=("Segoe UI", 10))
        subtitle.pack(anchor="w", pady=(4,0))

        # Control bar
        ctrl = tk.Frame(self.master, bg="#0f1117")
        ctrl.pack(fill="x", padx=18, pady=(8, 12))

        self.start_btn = tk.Button(ctrl, text="▶ Iniciar servidor pydoc",
                                   command=self.start_server, bg="#1f2937", fg="#e6eef8",
                                   activebackground="#374151", padx=12, pady=6, bd=0)
        self.start_btn.pack(side="left")

        self.stop_btn = tk.Button(ctrl, text="⏹ Detener servidor", command=self.stop_server,
                                  bg="#1f2937", fg="#e6eef8", activebackground="#374151", padx=12, pady=6, bd=0)
        self.stop_btn.pack(side="left", padx=(8,0))

        open_index_btn = tk.Button(ctrl, text="🌐 Abrir índice pydoc (root)", command=self.open_index,
                                   bg="#1f2937", fg="#e6eef8", padx=12, pady=6, bd=0)
        open_index_btn.pack(side="left", padx=(8,0))

        info_lbl = tk.Label(ctrl, text="(Asegúrate de que los módulos .py estén en esta carpeta o en PYTHONPATH)",
                            fg="#85909a", bg="#0f1117", font=("Segoe UI", 9))
        info_lbl.pack(side="right")

        # Grid of module buttons
        cards = tk.Frame(self.master, bg="#0f1117")
        cards.pack(fill="both", expand=True, padx=18, pady=(6,18))

        # arrange in grid: 3 columns
        cols = 3
        r = 0; c = 0
        for label, module_name in self.module_map.items():
            card = tk.Frame(cards, bg="#111216", bd=0, relief="flat", padx=12, pady=12)
            card.grid(row=r, column=c, padx=12, pady=12, sticky="nsew")
            cards.grid_columnconfigure(c, weight=1)

            title = tk.Label(card, text=label, fg="#cfe6ff", bg="#111216", font=("Segoe UI", 12, "bold"))
            title.pack(anchor="w")
            sub = tk.Label(card, text=f"module: {module_name}", fg="#9aa4b2", bg="#111216", font=("Segoe UI", 9))
            sub.pack(anchor="w", pady=(6,6))

            btn = tk.Button(card, text="Abrir documentación",
                            command=lambda m=module_name: self.open_module(m),
                            bg="#374151", fg="#e6eef8", bd=0, padx=8, pady=6, activebackground="#4b5563")
            btn.pack(anchor="e", pady=(8,0))

            c += 1
            if c >= cols:
                c = 0
                r += 1

        # Footer
        footer = tk.Frame(self.master, bg="#0f1117")
        footer.pack(fill="x", padx=18, pady=(0,12))
        foot_lbl = tk.Label(footer, text="© 2025 — Documentación técnica (pydoc). Pulsa Iniciar para arrancar servidor.",
                            fg="#6f7a84", bg="#0f1117", font=("Segoe UI", 9))
        foot_lbl.pack(anchor="e")

    # -------------------------
    # Acciones
    # -------------------------
    def start_server(self):
        if self.pydoc_proc is not None and self.pydoc_proc.poll() is None:
            messagebox.showinfo("Servidor pydoc", f"El servidor pydoc ya está corriendo en el puerto {self.pydoc_port}.")
            return
        try:
            ensure_cwd_in_path()
            self.pydoc_proc = start_pydoc_server(self.pydoc_port)
            # esperar un poco para que el servidor esté arriba
            time.sleep(STARTUP_WAIT)
            messagebox.showinfo("Servidor pydoc", f"Servidor pydoc iniciado en http://localhost:{self.pydoc_port}/")
        except Exception as e:
            messagebox.showerror("Error arrancando pydoc", str(e))

    def stop_server(self):
        if self.pydoc_proc is None:
            messagebox.showinfo("Servidor pydoc", "No hay servidor pydoc corriendo.")
            return
        stop_process(self.pydoc_proc)
        self.pydoc_proc = None
        messagebox.showinfo("Servidor pydoc", "Servidor detenido.")

    def open_module(self, module_name):
        # abrir doc; si servidor no está corriendo, arrancarlo automáticamente
        if self.pydoc_proc is None or (self.pydoc_proc and self.pydoc_proc.poll() is not None):
            # arrancar en background
            try:
                self.start_server()
            except Exception:
                pass
        # abrir la URL
        try:
            open_module_doc(module_name, host="localhost", port=self.pydoc_port)
        except Exception as e:
            messagebox.showerror("Error abriendo doc", str(e))

    def open_index(self):
        # Abre la raíz pydoc
        try:
            if self.pydoc_proc is None or (self.pydoc_proc and self.pydoc_proc.poll() is not None):
                self.start_server()
            webbrowser.open_new_tab(f"http://localhost:{self.pydoc_port}/")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        if self.pydoc_proc:
            stop_process(self.pydoc_proc)
        self.master.destroy()


# -------------------------
# EJECUCIÓN PRINCIPAL
# -------------------------
def main():
    # Ayuda: asegurar que el directorio actual esté en sys.path para que pydoc encuentre módulos locales
    ensure_cwd_in_path()

    root = tk.Tk()
    app = DocPortalApp(root, MODULE_MAP, pydoc_port=PYDOC_PORT)

    # Bind close to ensure subprocess killed
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()

if __name__ == "__main__":
    main()
