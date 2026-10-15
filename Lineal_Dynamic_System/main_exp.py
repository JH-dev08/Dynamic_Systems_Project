# DESARROLLADO POR: José Herrera Gómez, Samuel Porto Gómez
import math                                                                     # subprocess permite ejecutar procesos externos (Gnuplot) como archivos "script" desde Python.
import numpy as np
from scipy.linalg import expm
import subprocess                                                               # Hubo problemas con la librería PyGnuplot y permite enviar comandos directamente a Gnuplot.
import tkinter as tk
from tkinter import filedialog, messagebox

# Control del Proceso de Gnuplot mediante subprocess.
gnuplot_proc = None
ruta_gnuplot = r"C:\Program Files\gnuplot\bin\gnuplot.exe"                      # Permite abrir Gnuplot en Windows y acceder a la gráfica.

# Envía comandos de texto directamente al proceso de Gnuplot.
def enviar_gnuplot(comandos):
    global gnuplot_proc                                                         # global permite modificar la variable gnuplot_proc definida fuera de la función, para mantener el estado del proceso de Gnuplot entre llamadas.
    try:
        # Si el proceso no se ha iniciado o se cerró, lo vuelve a abrir
        if gnuplot_proc is None or gnuplot_proc.poll() is not None:
            gnuplot_proc = subprocess.Popen([ruta_gnuplot, "-p"], stdin=subprocess.PIPE, text=True)

        if isinstance(comandos, list):                                          # isinstance() verifica si la variable comandos es una lista.
            comandos = "\n".join(comandos)                                      # Convierte la lista en una cadena de texto unida por saltos de línea.

        if gnuplot_proc is not None and gnuplot_proc.stdin is not None:         # Evita el problema de validación de estado "NoneType" para los metodos "stdin".
            gnuplot_proc.stdin.write(comandos + "\n")                           # Envía los comandos a Gnuplot a través de la entrada estándar (stdin) del proceso.
            gnuplot_proc.stdin.flush()                                          # Asegura que los comandos se envíen inmediatamente al proceso de Gnuplot, sin esperar a que se llene el buffer.
    except Exception as e:
        messagebox.showerror(
            "Error de Gnuplot",
            f"No se pudo comunicar con Gnuplot.\nAsegúrate de que 'gnuplot' esté instalado y en el PATH del sistema.\n\nDetalle: {e}",
        )

# Crea el archivo "trayectorias.dat" si no existe y genera las coordenadas de las curvas de solución alrededor del origen a partir de los puntos iniciales.
def generar_archivo_trayectorias(
    a1, b1, a2, b2, archivo="trayectorias.dat"
):
    """Calcula las trayectorias exactas de forma analítica mediante e^(A*t)."""
    A = np.array([[a1, b1], [a2, b2]])

    puntos_iniciales = []
    for r in [0.8, 2.0, 3.5]:
        for i in range(12):
            angulo = i * (2 * math.pi / 12)
            puntos_iniciales.append(
                (r * math.cos(angulo), r * math.sin(angulo))
            )

    with open(archivo, "w") as f:
        for x0, y0 in puntos_iniciales:
            v0 = np.array([x0, y0])

            # Futuro (+t)
            for paso in range(120):
                t = paso * 0.03
                pos = expm(A * t) @ v0
                x, y = pos[0], pos[1]
                f.write(f"{x} {y}\n")
                if abs(x) > 6 or abs(y) > 6:
                    break
            f.write("\n\n")

            # Pasado (-t)
            for paso in range(120):
                t = -paso * 0.03
                pos = expm(A * t) @ v0
                x, y = pos[0], pos[1]
                f.write(f"{x} {y}\n")
                if abs(x) > 6 or abs(y) > 6:
                    break
            f.write("\n\n")

# Evalúa la unicidad y la naturaleza del punto crítico (0,0).
def clasificar_punto_critico(a1, b1, a2, b2):
    T = a1 + b2                                                                 # Traza
    D = a1 * b2 - b1 * a2                                                       # Determinante
    delta = T**2 - 4 * D                                                        # Discriminante

    # Limitante D == 0
    if abs(D) < 1e-9:
        return "EL PUNTO CRITICO (0,0) NO ES UNICO.", True

    if D < 0:
        naturaleza = "Punto de Silla (Inestable)"
    elif delta > 0:
        naturaleza = "Nodo Inestable" if T > 0 else "Nodo Estable"
    elif delta < 0:
        if T == 0:
            naturaleza = "Centro (Marginalmente Estable)"
        else:
            naturaleza = (
                "Foco / Espiral Inestable" if T > 0 else "Foco / Espiral Estable"
            )
    else:
        naturaleza = (
            "Nodo Degenerado Inestable" if T > 0 else "Nodo Degenerado Estable"
        )

    return f"Naturaleza: {naturaleza}", False


# Actualización dinamica al escribir los datos.
def actualizar_calculo(*args):
    try:
        val_a1 = float(var_a1.get())
        val_b1 = float(var_b1.get())
        val_a2 = float(var_a2.get())
        val_b2 = float(var_b2.get())

        resultado, no_unico = clasificar_punto_critico(
            val_a1, val_b1, val_a2, val_b2
        )

        if no_unico:
            lbl_resultado.config(text=resultado, fg="red")
        else:
            lbl_resultado.config(text=resultado, fg="blue")

        generar_archivo_trayectorias(val_a1, val_b1, val_a2, val_b2)
        dibujar_sistema(val_a1, val_b1, val_a2, val_b2, resultado)

    except ValueError:
        lbl_resultado.config(text="Esperando los 4 parámetros...", fg="gray")

# Genera la lista de comandos para Gnuplot.
def construir_script_gnuplot(a1, b1, a2, b2, titulo):
    return [
        f'set title "{titulo}"',                                                # Define el título del gráfico en Gnuplot, que mostrará la naturaleza del punto crítico.
        f"a1={a1}; b1={b1}; a2={a2}; b2={b2}",                                  # Define las variables a1, b1, a2 y b2 y su valor actual en Gnuplot.
        "set xrange [-5:5]",                                                    # Define los límites del eje x e y para el gráfico, estableciendo un rango de -5 a 5 en ambos ejes.
        "set yrange [-5:5]",
        "set samples 18",                                                       # Define la cantidad de muestras para el campo vectorial, afectando la densidad de las flechas.
        "set isosamples 18",                                                    # Define la cantidad de muestras para el campo vectorial, afectando la densidad de las flechas.
        "set grid",                                                             # Activa la cuadrícula en el gráfico para facilitar la visualización de las trayectorias y el campo vectorial.
        "set key bottom right",                                                 # Posiciona la leyenda en la parte inferior derecha del gráfico.
        "dx(x,y) = a1*x + b1*y",                                                # Define las funciones dx y dy que representan el sistema de ecuaciones diferenciales lineales.
        "dy(x,y) = a2*x + b2*y",

        # Dibuja el campo vectorial y las trayectorias.
        'plot "++" using 1:2:(dx($1,$2)*0.12):(dy($1,$2)*0.12) with vectors head filled linecolor rgb "#A0A0A0" title "Campo Vectorial", '
        '"trayectorias.dat" with lines linecolor rgb "#0066FF" lw 1.5 title "Trayectorias"',
    ]

# Envía los comandos de renderizado.
def dibujar_sistema(a1, b1, a2, b2, titulo):
    cmds = construir_script_gnuplot(a1, b1, a2, b2, titulo)
    enviar_gnuplot(cmds)

# Guarda una copia del gráfico actual en disco (PNG o PDF).
def exportar_grafico():
    try:
        val_a1 = float(var_a1.get())
        val_b1 = float(var_b1.get())
        val_a2 = float(var_a2.get())
        val_b2 = float(var_b2.get())
    except ValueError:
        messagebox.showwarning(
            "Atención",
            "Debe ingresar los 4 parámetros válidos antes de exportar.",
        )
        return

    archivo = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("Imagen PNG", "*.png"),
            ("Documento PDF", "*.pdf"),
            ("Todos los archivos", "*.*"),
        ],
        title="Guardar gráfico como...",
    )

    if archivo:
        # Formatear ruta para compatibilidad con Gnuplot en Windows
        archivo_clean = archivo.replace("\\", "/")
        resultado, _ = clasificar_punto_critico(val_a1, val_b1, val_a2, val_b2)

        cmds = ["set terminal push"]                                           # Guarda la configuración actual del terminal para restaurarla después de exportar.
        if archivo_clean.lower().endswith(".pdf"):
            cmds.append("set terminal pdf color solid size 6,5")
        else:
            cmds.append("set terminal png size 800,600")

        cmds.append(f'set output "{archivo_clean}"')
        cmds.extend(
            construir_script_gnuplot(
                val_a1, val_b1, val_a2, val_b2, resultado
            )
        )
        cmds.append("set output")
        cmds.append("set terminal pop")

        enviar_gnuplot(cmds)
        messagebox.showinfo(
            "Éxito", f"Gráfico exportado correctamente en:\n{archivo}"
        )

# Limpia todos los campos de texto y resetea el programa.
def limpiar_campos():
    var_a1.set("")
    var_b1.set("")
    var_a2.set("")
    var_b2.set("")
    lbl_resultado.config(text="Esperando los 4 parámetros...", fg="gray")
    enviar_gnuplot(["clear", "reset"])

# Restringe la entrada solo a valores numéricos.
def validar_entrada(texto):
    if texto in ("", "-", ".", "-."):
        return True
    try:
        float(texto)
        return True
    except ValueError:
        return False
# ======================================================================================================================================================================================================== #

# --- CONSTRUCCIÓN DE LA INTERFAZ GRÁFICA ---
ventana = tk.Tk()                                                               # Crea la ventana principal.
ventana.title("Análisis de Sistemas Dinámicos Lineales")
ventana.geometry("400x320")
ventana.resizable(True,True)                                                    # Permite redimensionar la ventana.

# BODY DEL PROGRAMA                                                             # "ventana.register()"" es un método para registrar la función de validación para las entradas de texto.
validacion = (ventana.register(validar_entrada), "%P")                          # "%P" es un marcador de posición que representa el valor actual del campo de entrada antes de la validación.

# Definición de variables reactivas para los parámetros del sistema.
var_a1 = tk.StringVar()                                                         # tk.StringVar() es una clase de Tkinter que permite crear variables de tipo cadena observables para cambios.
var_b1 = tk.StringVar()
var_a2 = tk.StringVar()
var_b2 = tk.StringVar()

for v in (var_a1, var_b1, var_a2, var_b2):                                      # Llama a la función "actualizar_calculo" cada vez que se modifique alguna de las variables.
    v.trace_add("write", actualizar_calculo)                                    # Metodo "trace_add()"" permite asociar una función a un evento de cambio en la variable.

# Formulario de Ecuaciones
tk.Label(
    ventana, text="Ecuaciones del Sistema:", font=("Arial", 15, "bold")
).pack()                                                                        # pack() organiza los widgets en bloques.

# Frame para la ecuación x'
frame_eq1 = tk.Frame(ventana)                                                   # tk.Frame() es un contenedor que permite organizar los widgets dentro de la ventana principal.
frame_eq1.pack(pady=5)
tk.Label(frame_eq1, text="x' =").pack(side=tk.LEFT)
tk.Entry(
    frame_eq1,
    textvariable=var_a1,                                                        # Indica que el contenido se guarda en la variable var_a1.
    validate="key",                                                             # Indica que la validación se realizará en cada pulsación de tecla.
    validatecommand=validacion,                                                 # Indica que la función de validación será la definida anteriormente.
    width=6,
).pack(side=tk.LEFT)

tk.Label(frame_eq1, text="x +").pack(side=tk.LEFT)
tk.Entry(
    frame_eq1,
    textvariable=var_b1,
    validate="key",
    validatecommand=validacion,
    width=6,
).pack(side=tk.LEFT)
tk.Label(frame_eq1, text="y").pack(side=tk.LEFT)

# Frame para la ecuación y'
frame_eq2 = tk.Frame(ventana)
frame_eq2.pack(pady=5)

tk.Label(frame_eq2, text="y' =").pack(side=tk.LEFT)
tk.Entry(
    frame_eq2,
    textvariable=var_a2,
    validate="key",
    validatecommand=validacion,
    width=6,
).pack(side=tk.LEFT)

tk.Label(frame_eq2, text="x +").pack(side=tk.LEFT)
tk.Entry(
    frame_eq2,
    textvariable=var_b2,
    validate="key",
    validatecommand=validacion,
    width=6,
).pack(side=tk.LEFT)
tk.Label(frame_eq2, text="y").pack(side=tk.LEFT)

# Etiqueta de Clasificación
lbl_resultado = tk.Label(
    ventana,
    text="Esperando los 4 parámetros...",
    font=("Arial", 10, "bold"),
    fg="gray",
    wraplength=360,
)
lbl_resultado.pack(pady=15)

# Panel Inferior de Botones
frame_botones = tk.Frame(ventana)
frame_botones.pack(pady=10)

btn_exportar = tk.Button(
    frame_botones,
    text="Exportar Gráfico",
    command=exportar_grafico,                                                   # Llama a la función exportar_grafico() al hacer clic en el botón.
    bg="#4CAF50",
    fg="white",
    font=("Arial", 9, "bold"),
    padx=10,
)
btn_exportar.pack(side=tk.LEFT, padx=5)

btn_limpiar = tk.Button(
    frame_botones,
    text="Limpiar",
    command=limpiar_campos,                                                     # Llama a la función limpiar_campos() al hacer clic en el botón.
    bg="#f44336",
    fg="white",
    font=("Arial", 9, "bold"),
    padx=10,
)
btn_limpiar.pack(side=tk.LEFT, padx=5)

# Inicia el bucle principal de la interfaz gráfica hasta que se cierre.
ventana.mainloop()