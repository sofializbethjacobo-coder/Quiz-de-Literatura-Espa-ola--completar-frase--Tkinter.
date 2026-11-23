# "Quiz de Literatura Española (completar frase) - Tkinter."
#OBJETIVO: desarrollar un juego de preguntas y respuestas sobre literatura española, donde el jugador debe completar frases con la palabra correcta. El juego utiliza una interfaz gráfica creada con Tkinter y lee las preguntas desde un archivo CSV.
#PROYECTO FINAL  DE LENJUAJES DE PROGRAMACION 1
#NOMBRE:Sofia Lizeth Jacobo Cuaya 
# MATRICULA: 202608406
import csv
import os
import random
import tkinter as tk
from tkinter import messagebox

ARCHIVO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preguntas.csv")
NUM_PREGUNTAS = 3
PTS_ESCRITA = 10
PTS_LISTA = 5
FUENTE = ("Times New Roman", 16)
COLOR_TEXTO = "#000000"


def normalizar(texto):
    """strip + lower; las tildes se conservan."""
    return texto.strip().lower()


def cargar_preguntas(ruta=ARCHIVO):
    "Lee TODAS las preguntas del CSV: lista de (frase, respuesta)."
    preguntas = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.reader(f):
            if len(fila) < 2:
                continue
            frase, palabra = fila[0].strip(), fila[1].strip()
            if frase and palabra and frase != "frase_incompleta":
                preguntas.append((frase, palabra))
    return preguntas


def opciones_para(correcta, todas, cantidad=5):
    "Respuesta correcta + distractores tomados de las demás respuestas."
    otras = list({p for _, p in todas if normalizar(p) != normalizar(correcta)})
    random.shuffle(otras)
    opciones = [correcta] + otras[: cantidad - 1]
    random.shuffle(opciones)
    return opciones


def evaluar(entry_texto, seleccion, correcta):
    """Devuelve (puntos, respuesta_usada). El Entry tiene prioridad."""
    if normalizar(entry_texto):
        usada, pts = entry_texto.strip(), PTS_ESCRITA
    elif seleccion:
        usada, pts = seleccion, PTS_LISTA
    else:
        return None, None
    acierto = normalizar(usada) == normalizar(correcta)
    return (pts if acierto else 0), usada


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Quiz de Literatura Española")
        self.geometry("720x460")
        self.resizable(False, False)
        self.nombre = ""
        self.todas = []
        self.juego = []
        self.indice = 0
        self.puntaje = 0
        self.aciertos = 0
        self.vista = None
        self.configure(bg="lightgreen")
        self.option_add("*Frame.Background", "lightgreen")
        self.option_add("*Label.Background", "lightgreen")
        self.vista_inicio()

    def cambiar_vista(self):
        if self.vista is not None:
            self.vista.destroy()
        self.vista = tk.Frame(self, padx=20, pady=20)
        self.vista.pack(fill="both", expand=True)
        return self.vista

    #  Vista 1: Inicio 
    def vista_inicio(self):
        f = self.cambiar_vista()
        tk.Label(f, text="Quiz de Literatura Española",
                 font=("Times New Roman", 24, "bold"), fg=COLOR_TEXTO).pack(pady=(40, 20))
        tk.Label(f, text="Nombre del jugador:", font=FUENTE, fg=COLOR_TEXTO).pack()
        self.entry_nombre = tk.Entry(f, font=FUENTE, width=25, justify="center")
        self.entry_nombre.pack(pady=10)
        self.entry_nombre.focus()
        tk.Button(f, text="Comenzar", font=FUENTE, command=self.comenzar).pack(pady=20)
        self.bind("<Return>", lambda e: self.comenzar())

    def comenzar(self):
        nombre = self.entry_nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Aviso", "Escribe tu nombre para comenzar.")
            return
        try:
            self.todas = cargar_preguntas()
        except (OSError, csv.Error) as e:
            messagebox.showerror("Error", f"No se pudo leer preguntas.csv:\n{e}")
            return
        if len(self.todas) < NUM_PREGUNTAS:
            messagebox.showerror(
                "Error",
                f"El archivo tiene {len(self.todas)} preguntas; se necesitan al "
                f"menos {NUM_PREGUNTAS}. El juego no puede iniciar.")
            return
        self.nombre = nombre
        self.juego = random.sample(self.todas, NUM_PREGUNTAS)
        self.indice = 0
        self.puntaje = 0
        self.aciertos = 0
        self.unbind("<Return>")
        self.vista_juego()

    #  Vista 2: Juego 
    def vista_juego(self):
        frase, correcta = self.juego[self.indice]
        f = self.cambiar_vista()
        f.columnconfigure(0, weight=1)
        f.columnconfigure(1, weight=1)

        tk.Label(f, text=f"Jugador: {self.nombre}   |   Pregunta "
                         f"{self.indice + 1}/{NUM_PREGUNTAS}   |   Puntaje: {self.puntaje}",
                 font=("Times New Roman", 12), fg=COLOR_TEXTO
                 ).grid(row=0, column=0, columnspan=2, sticky="w")

        tk.Label(f, text=frase, font=FUENTE, fg=COLOR_TEXTO, wraplength=660,
                 justify="center").grid(row=1, column=0, columnspan=2, pady=20)

        tk.Label(f, text=f"Escribe la palabra ({PTS_ESCRITA} pts):",
                 font=("Times New Roman", 13)).grid(row=2, column=0, sticky="w")
        tk.Label(f, text=f"O elígela de la lista ({PTS_LISTA} pts):",
                 font=("Times New Roman", 13)).grid(row=2, column=1, sticky="w")

        self.entry_resp = tk.Entry(f, font=FUENTE, width=24)
        self.entry_resp.grid(row=3, column=0, sticky="nw", pady=5)
        self.entry_resp.focus()

        self.lista = tk.Listbox(f, font=FUENTE, height=5, exportselection=False)
        for op in opciones_para(correcta, self.todas):
            self.lista.insert("end", op)
        self.lista.grid(row=3, column=1, sticky="nw", pady=5)

        tk.Button(f, text="Validar", font=FUENTE, command=self.validar
                  ).grid(row=4, column=0, columnspan=2, pady=20)
        self.bind("<Return>", lambda e: self.validar())

    def validar(self):
        frase, correcta = self.juego[self.indice]
        sel = self.lista.curselection()
        seleccion = self.lista.get(sel[0]) if sel else ""
        pts, usada = evaluar(self.entry_resp.get(), seleccion, correcta)
        if pts is None:
            messagebox.showwarning("Aviso", "Escribe una respuesta o selecciona una opción.")
            return
        if pts > 0:
            self.puntaje += pts
            self.aciertos += 1
            messagebox.showinfo("¡Correcto!", f"+{pts} puntos")
        else:
            messagebox.showinfo("Incorrecto", f"La respuesta correcta era: {correcta}")
        self.indice += 1
        if self.indice < NUM_PREGUNTAS:
            self.vista_juego()
        else:
            self.unbind("<Return>")
            self.vista_resultados()

    # Vista 3: Resultados 
    def vista_resultados(self):
        f = self.cambiar_vista()
        tk.Label(f, text="Resultados", font=("Times New Roman", 24, "bold"),
                 fg=COLOR_TEXTO).pack(pady=(40, 10))
        tk.Label(f, text=f"Jugador: {self.nombre}", font=FUENTE, fg=COLOR_TEXTO).pack()
        tk.Label(f, text=f"Puntaje: {self.puntaje} pts", font=FUENTE, fg=COLOR_TEXTO).pack(pady=5)
        tk.Label(f, text=f"Respuestas correctas: {self.aciertos} de {NUM_PREGUNTAS}",
                 font=FUENTE, fg=COLOR_TEXTO).pack(pady=5)
        tk.Button(f, text="Jugar de nuevo", font=FUENTE, command=self.vista_inicio).pack(pady=15)
        tk.Button(f, text="Salir", font=FUENTE, command=self.confirmar_salida).pack()
        messagebox.showinfo("Fin del juego",
                            f"{self.nombre}, obtuviste {self.puntaje} puntos "
                            f"({self.aciertos}/{NUM_PREGUNTAS} correctas).")

    def confirmar_salida(self):
        if messagebox.askyesno("Salir", "¿Seguro que quieres salir?"):
            self.destroy()


if __name__ == "__main__":
 App().mainloop()
