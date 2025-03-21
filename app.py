#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Fast Server 1.0
# Written by Ismael Heredia
# python -m pip install ttkbootstrap

import os
import shutil
import subprocess
import threading
import ttkbootstrap as tb
from tkinter import filedialog, StringVar, Text, Scrollbar, END, messagebox, DISABLED, NORMAL

def seleccionar_carpeta(variable):
    carpeta = filedialog.askdirectory()
    if carpeta:
        variable.set(carpeta)

def generar_servidor():
    carpeta_dist = carpeta_var.get()
    carpeta_destino = carpeta_destino_var.get()
    framework = framework_var.get()
    puerto = puerto_var.get()
    
    if not carpeta_dist or not carpeta_destino or framework not in ["React", "VueJS", "Angular"]:
        actualizar_consola("Selecciona una carpeta de origen, destino y un framework válido\n")
        return
    
    if not puerto.isdigit():
        actualizar_consola("El puerto debe ser un número\n")
        return

    puerto = int(puerto)

    try:
        if os.path.exists(carpeta_destino):
            shutil.rmtree(carpeta_destino)
        os.makedirs(carpeta_destino)

        actualizar_consola("Copiando archivos ...\n")
        
        if framework == "Angular":
            carpeta_browser = os.path.join(carpeta_dist, "browser")
            if os.path.exists(carpeta_browser):
                shutil.copytree(carpeta_browser, os.path.join(carpeta_destino, "browser"))
                carpeta_servida = "browser"
            else:
                shutil.copytree(carpeta_dist, os.path.join(carpeta_destino, "dist"))
                carpeta_servida = "dist"
        else:
            shutil.copytree(carpeta_dist, os.path.join(carpeta_destino, "dist"))
            carpeta_servida = "dist"

        package_json = """{
            "name": "generated-server",
            "version": "1.0.0",
            "description": "Servidor Node.js",
            "main": "app.js",
            "scripts": {
                "start": "node app.js"
            },
            "dependencies": {
                "express": "^4.18.2"
            }
        }"""

        with open(os.path.join(carpeta_destino, "package.json"), "w", encoding="utf-8") as f:
            f.write(package_json)

        index_file = "index.csr.html" if framework == "Angular" else "index.html"

        app_js = f"""const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || {puerto};

app.use(express.static(path.join(__dirname, "{carpeta_servida}")));

app.get("*", (req, res) => {{
    res.sendFile(path.join(__dirname, "{carpeta_servida}", "{index_file}"));
}});

app.listen(PORT, () => {{
    console.log(`Servidor activo en http://localhost:${{PORT}}`);
}});"""

        with open(os.path.join(carpeta_destino, "app.js"), "w", encoding="utf-8") as f:
            f.write(app_js)

        actualizar_consola("Archivos generados correctamente\n")
        
        threading.Thread(target=instalar_dependencias, args=(carpeta_destino,), daemon=True).start()
    except Exception as e:
        actualizar_consola(f"Error: {str(e)}\n")

def instalar_dependencias(carpeta_destino):
    actualizar_consola("Ejecutando npm install ...\n")

    try:
        process = subprocess.Popen("npm install", shell=True, cwd=carpeta_destino, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = process.communicate()

        if stdout:
            actualizar_consola(stdout)
        if stderr:
            actualizar_consola(stderr)

        actualizar_consola("Instalación completada. Ejecuta el servidor con 'node app.js'\n")

        messagebox.showinfo("Proceso finalizado", "El servidor se ha generado correctamente.")
        
    except Exception as e:
        actualizar_consola(f"Error en npm install: {str(e)}\n")

def actualizar_consola(texto):
    consola.config(state=NORMAL)
    consola.insert(END, texto)
    consola.config(state=DISABLED) 
    consola.yview_moveto(1)

root = tb.Window(themename="superhero")
root.title("Fast Server 1.0 | Copyright (C) 2025 Ismael Heredia")
root.geometry("720x500")
root.resizable(False, False)

carpeta_var = StringVar()
carpeta_destino_var = StringVar()
framework_var = StringVar()
puerto_var = StringVar()

tb.Label(root, text="Seleccione la carpeta dist:").place(x=20, y=20)
tb.Entry(root, textvariable=carpeta_var, width=45).place(x=210, y=20)
tb.Button(root, text="Examinar", command=lambda: seleccionar_carpeta(carpeta_var)).place(x=610, y=20)

tb.Label(root, text="Seleccione la carpeta destino:").place(x=20, y=60)
tb.Entry(root, textvariable=carpeta_destino_var, width=45).place(x=210, y=60)
tb.Button(root, text="Examinar", command=lambda: seleccionar_carpeta(carpeta_destino_var)).place(x=610, y=57)

tb.Label(root, text="Seleccione el framework:").place(x=20, y=100)
tb.Combobox(root, textvariable=framework_var, values=["React", "VueJS", "Angular"]).place(x=210, y=100)

tb.Label(root, text="Seleccione el puerto:").place(x=20, y=140)
tb.Entry(root, textvariable=puerto_var, width=10).place(x=210, y=140)

frame_consola = tb.Frame(root)
frame_consola.place(x=20, y=190)
scrollbar = Scrollbar(frame_consola)
consola = Text(frame_consola, height=10, width=83, state=DISABLED, yscrollcommand=scrollbar.set)
scrollbar.config(command=consola.yview)
scrollbar.pack(side="right", fill="y")
consola.pack(side="left", fill="both", expand=True)

tb.Button(root, text="Generar servidor", command=generar_servidor, bootstyle="success").place(x=250, y=430, width=200, height=35)

root.mainloop()
