import os
import json
import requests
from deep_translator import GoogleTranslator
import customtkinter as ctk
from tkinter import messagebox

# Diccionario ampliado para pronunciación simplificada
PRONUNCIACION_SIMPLE = {
    "hello": "jelou",
    "world": "wuorld",
    "from": "from",
    "the": "de",
    "other": "oder",
    "side": "said",
    "love": "lov",
    "night": "nait",
    "day": "dei",
    "heart": "jart",
    "time": "taim",
    "dream": "drim",
    "forever": "forever",
}

# Archivo para guardar canciones
ARCHIVO_CANCIONES = "canciones_guardadas.json"

# Función para buscar la letra
def buscar_letra(nombre_cancion, artista=""):
    url = f"https://api.lyrics.ovh/v1/{artista}/{nombre_cancion}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("lyrics", "Letra no encontrada.")
    else:
        return "No se encontró la canción."

# Función para traducir un verso
def traducir_verso(verso):
    traductor = GoogleTranslator(source='en', target='es')
    return traductor.translate(verso)

# Función para obtener pronunciación simplificada
def obtener_pronunciacion_simple(verso):
    palabras = verso.split()
    pronunciacion = [PRONUNCIACION_SIMPLE.get(palabra.lower(), palabra) for palabra in palabras]
    return " ".join(pronunciacion)

# Función para guardar canción en archivo
def guardar_cancion(nombre_cancion, artista, letra, traduccion, pronunciacion):
    datos = {
        "artista": artista,
        "letra": letra,
        "traduccion": traduccion,
        "pronunciacion": pronunciacion,
    }
    canciones = cargar_canciones()
    canciones[nombre_cancion] = datos
    with open(ARCHIVO_CANCIONES, "w", encoding="utf-8") as archivo:
        json.dump(canciones, archivo, ensure_ascii=False, indent=4)

# Función para cargar canciones guardadas
def cargar_canciones():
    if os.path.exists(ARCHIVO_CANCIONES):
        with open(ARCHIVO_CANCIONES, "r", encoding="utf-8") as archivo:
            return json.load(archivo)
    return {}

# Función principal para procesar la canción
def procesar_cancion():
    nombre_cancion = entrada_cancion.get().strip()
    artista = entrada_artista.get().strip()
    
    if not nombre_cancion:
        messagebox.showerror("Error", "Por favor, ingresa el nombre de la canción.")
        return

    # Revisar si la canción ya está guardada
    canciones = cargar_canciones()
    if nombre_cancion in canciones:
        datos = canciones[nombre_cancion]
        mostrar_resultados(datos["letra"], datos["traduccion"], datos["pronunciacion"])
        return

    # Buscar la letra
    letra_original = buscar_letra(nombre_cancion, artista)
    if letra_original == "No se encontró la canción.":
        messagebox.showerror("Error", "No se encontró la canción. Verifica el nombre o el artista.")
        return

    # Procesar letra
    versos = letra_original.split('\n')
    traducciones = []
    pronunciaciones = []
    for verso in versos:
        if verso.strip():
            traducciones.append(traducir_verso(verso))
            pronunciaciones.append(obtener_pronunciacion_simple(verso))

    # Mostrar resultados
    mostrar_resultados(letra_original, "\n".join(traducciones), "\n".join(pronunciaciones))

    # Guardar resultados
    guardar_cancion(nombre_cancion, artista, letra_original, "\n".join(traducciones), "\n".join(pronunciaciones))

# Función para mostrar resultados en la interfaz
def mostrar_resultados(letra, traduccion, pronunciacion):
    texto_resultado.delete(1.0, ctk.END)
    texto_resultado.insert(ctk.END, f"=== Letra Original ===\n{letra}\n\n")
    texto_resultado.insert(ctk.END, f"=== Traducción ===\n{traduccion}\n\n")
    texto_resultado.insert(ctk.END, f"=== Pronunciación ===\n{pronunciacion}\n")

# Función para ver canciones guardadas
def cargar_canciones_guardadas():
    canciones = cargar_canciones()
    if not canciones:
        messagebox.showinfo("Canciones Guardadas", "No hay canciones guardadas aún.")
        return
    
    # Crear una nueva ventana para seleccionar canciones guardadas
    ventana_canciones = ctk.CTkToplevel(ventana)
    ventana_canciones.title("Canciones Guardadas")
    ventana_canciones.geometry("400x400")

    ctk.CTkLabel(ventana_canciones, text="Selecciona una canción guardada:").pack(pady=10)

    # Lista de canciones
    lista_canciones = ctk.CTkListbox(ventana_canciones)
    lista_canciones.pack(fill="both", expand=True, pady=10)

    # Agregar canciones a la lista
    for cancion in canciones.keys():
        lista_canciones.insert("end", cancion)

    # Botón para cargar la canción seleccionada
    def cargar_cancion_seleccionada():
        seleccion = lista_canciones.get(lista_canciones.curselection())
        datos = canciones[seleccion]
        mostrar_resultados(datos["letra"], datos["traduccion"], datos["pronunciacion"])
        ventana_canciones.destroy()

    ctk.CTkButton(ventana_canciones, text="Cargar Canción", command=cargar_cancion_seleccionada).pack(pady=10)

# Configuración de la interfaz
ctk.set_appearance_mode("dark")  # Modo oscuro
ctk.set_default_color_theme("blue")  # Tema azul

ventana = ctk.CTk()
ventana.title("Aplicación de Música")
ventana.geometry("900x900")

# Etiquetas y entradas
ctk.CTkLabel(ventana, text="Nombre de la canción:").pack(pady=5)
entrada_cancion = ctk.CTkEntry(ventana, width=400)
entrada_cancion.pack(pady=5)

ctk.CTkLabel(ventana, text="Artista (opcional):").pack(pady=5)
entrada_artista = ctk.CTkEntry(ventana, width=400)
entrada_artista.pack(pady=5)

# Botón para procesar
boton_procesar = ctk.CTkButton(ventana, text="Procesar Canción", command=procesar_cancion)
boton_procesar.pack(pady=10)

# Botón para ver canciones guardadas
boton_ver_guardadas = ctk.CTkButton(ventana, text="Ver Canciones Guardadas", command=cargar_canciones_guardadas)
boton_ver_guardadas.pack(pady=10)

# Texto para mostrar resultados
texto_resultado = ctk.CTkTextbox(ventana, wrap="word", height=450, width=450)
texto_resultado.pack(pady=10)

# Iniciar el loop de la interfaz
ventana.mainloop()
