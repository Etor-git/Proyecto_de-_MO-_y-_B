"""
sorting_gui.py

Versión final para presentación — interfaz con tkinter que:
- Carga datos desde .xlsx, .csv o .txt (hasta 10000 registros).
- Menú principal: Mostrar, Ordenar, Buscar, Salir.
- Mostrar permite ver registros antes y después de ordenar (Treeview).
- Ordenar abre submenú con métodos principales (QuickSort, MergeSort, Aleatorio) y Avanzado para los otros.
- Al completar el ordenamiento se muestra la leyenda:
  "Ordenado por el método XX y se realizó en XX nanosegundos".
- No muestra automáticamente los datos después de ordenar; para verlos usar Mostrar.
- Medición detallada (ns) y opción de guardar resultados a Excel.
- Registro de acciones y modificaciones en `mod_log.txt`.
- Cabecera con datos de identificación del equipo (Equipo 14 - Energía - Héctor Jesús Valadez Pardo y Alberto Roman Campos).

Dependencias (Librerias):
 pip install pandas openpyxl matplotlib

Uso:
 python sorting_gui.py

Notas:
 - El programa evita errores con try/except y validaciones.
 - Está escrito y etiquetado en español sin faltas de ortografía.
"""

import time
import random
import heapq
import traceback
from datetime import datetime
import numpy as np
import os
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --------------------------- Configuración ---------------------------------
EXCEL_OUTPUT = 'sorted_results_by_method.xlsx'
LOG_FILE = 'mod_log.txt'
MAX_RECORDS = 100000
TEAM_INFO = {
    'equipo': 'Equipo 14 - Energía',
    'integrantes': ['Héctor Jesús Valadez Pardo y Alberto Roman Campos'],
    'tema': 'Métodos de Ordenación y Búsqueda'
}

# --------------------------- Utilidades -----------------------------------

def registrar_log(mensaje: str):
    """
    Registra mensajes SIN fecha ni hora.
    """
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(mensaje + "\n")


# --------------------------- Instrumentación -------------------------------
class Profiler:
    def __init__(self):
        self.ops = 0
        self.history = []  # lista de (ops, segundos_transcurridos)
        self.start = None

    def start_timing(self):
        self.start = time.perf_counter()
        self.record()

    def op(self, count=1):
        self.ops += count
        # record periodically
        if self.ops % 50 == 0:
            self.record()

    def record(self):
        if self.start is None:
            t = 0.0
        else:
            t = time.perf_counter() - self.start
        self.history.append((self.ops, t))

    def finish(self):
        self.record()


# --------------------------- Algoritmos -----------------------------------
# Cada algoritmo toma (arr, profiler) y devuelve una lista ordenada.

# Función auxiliar para normalizar los datos
def normalizar_datos(arr):
    """
    Convierte los datos a un formato comparable (números, fechas o texto).
    Detecta automáticamente el tipo de dato dominante en la columna.
    """
    serie = pd.Series(arr)

    # Intentar conversión numérica (enteros o flotantes)
    num = pd.to_numeric(serie, errors='coerce')
    if num.notna().sum() > len(serie) * 0.6:  # mayoría numérica
        return num.fillna(method='ffill').astype(float).tolist()

    # Intentar conversión a fechas (YYYY/MM/DD, DD-MM-YYYY, etc.)
    fechas = pd.to_datetime(serie, errors='coerce', infer_datetime_format=True)
    if fechas.notna().sum() > len(serie) * 0.6:  # mayoría son fechas
        return fechas.map(lambda x: x.timestamp() if not pd.isna(x) else 0).tolist()

    # Si no son numéricos ni fechas, tratarlos como texto
    return serie.astype(str).str.lower().tolist()


#Bubble sort
def bubble_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    n = len(a)
    profiler.start_timing()
    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            profiler.op()
            if a[j] > a[j + 1]:
                a[j], a[j + 1] = a[j + 1], a[j]
                swapped = True
                profiler.op(5)
        if not swapped:
            break
    profiler.finish()
    return a


#Selection sort
def selection_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    n = len(a)
    profiler.start_timing()
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            profiler.op()
            if a[j] < a[min_idx]:
                min_idx = j
        if min_idx != i:
            a[i], a[min_idx] = a[min_idx], a[i]
            profiler.op(5)
    profiler.finish()
    return a


#Insertion sort
def insertion_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
            profiler.op(2)
        a[j + 1] = key
        profiler.op()
    profiler.finish()
    return a


#Shell sort
def shell_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    n = len(a)
    gap = n // 2
    profiler.start_timing()
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap and a[j - gap] > temp:
                a[j] = a[j - gap]
                j -= gap
                profiler.op(2)
            a[j] = temp
            profiler.op()
        gap //= 2
    profiler.finish()
    return a


#Merge sort
def merge_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()

    def merge(l):
        if len(l) <= 1:
            return l
        mid = len(l) // 2
        left = merge(l[:mid])
        right = merge(l[mid:])
        merged = []
        i = j = 0
        while i < len(left) and j < len(right):
            profiler.op()
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        merged.extend(left[i:])
        merged.extend(right[j:])
        return merged

    res = merge(a)
    profiler.finish()
    return res


#Quick Sort
def quick_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()

    # QuickSort iterativo: evita desbordamiento de recursión
    stack = [(0, len(a) - 1)]
    while stack:
        low, high = stack.pop()
        if low < high:
            pivot_index = random.randint(low, high)
            a[pivot_index], a[high] = a[high], a[pivot_index]
            pivot = a[high]
            i = low
            for j in range(low, high):
                profiler.op()
                if a[j] < pivot:
                    a[i], a[j] = a[j], a[i]
                    i += 1
            a[i], a[high] = a[high], a[i]

            # Apilar los subrangos (primero el más pequeño para menor profundidad)
            if i - 1 - low < high - (i + 1):
                stack.append((i + 1, high))
                stack.append((low, i - 1))
            else:
                stack.append((low, i - 1))
                stack.append((i + 1, high))

    profiler.finish()
    return a


#Heap sort
def heap_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()
    heap = []
    for x in a:
        heapq.heappush(heap, x)
        profiler.op()
    res = [heapq.heappop(heap) for _ in range(len(heap))]
    profiler.finish()
    return res


#Counting sort
def counting_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()

    # Validar tipo
    if not all(isinstance(x, (int, float)) for x in a):
        # Si no son números, usar ordenamiento estable por Python
        profiler.finish()
        return sorted(a, key=str)

    # Limitar rango
    mn, mx = int(min(a)), int(max(a))
    if mx - mn > 10_000_000:
        profiler.finish()
        return sorted(a)

    count = [0] * (mx - mn + 1)
    for v in a:
        count[int(v) - mn] += 1
        profiler.op()

    res = []
    for i, c in enumerate(count):
        if c:
            res.extend([i + mn] * c)
    profiler.finish()
    return res


#Radix Sort
def radix_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()

    # Si no son todos enteros o flotantes, usar ordenamiento por texto
    if not all(isinstance(x, (int, float)) for x in a):
        profiler.finish()
        return sorted(a, key=str)

    a = [int(x) for x in a]
    maxv = max(a)
    exp = 1
    while maxv // exp > 0:
        buckets = [[] for _ in range(10)]
        for num in a:
            idx = (num // exp) % 10
            buckets[idx].append(num)
            profiler.op()
        a = [num for bucket in buckets for num in bucket]
        exp *= 10
    profiler.finish()
    return a


#Bucket sort
def bucket_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    profiler.start_timing()

    # Si los datos no son numéricos, ordenar como texto
    if not all(isinstance(x, (int, float)) for x in a):
        profiler.finish()
        return sorted(a, key=str)

    n = len(a)
    if n == 0:
        profiler.finish()
        return []

    mn, mx = min(a), max(a)
    if mn == mx:
        profiler.finish()
        return a.copy()

    # Crear cubetas proporcionales al rango
    buckets = [[] for _ in range(n)]
    for x in a:
        idx = int((x - mn) / (mx - mn + 1e-9) * (n - 1))
        buckets[idx].append(x)
        profiler.op()

    res = []
    for b in buckets:
        b.sort()
        res.extend(b)
    profiler.finish()
    return res


#Cocktail sort
def cocktail_sort(arr, profiler: Profiler):
    datos = normalizar_datos(arr)
    a = datos.copy()
    n = len(a)
    swapped = True
    start = 0
    end = n - 1
    profiler.start_timing()
    while swapped:
        swapped = False
        for i in range(start, end):
            profiler.op()
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
                profiler.op(3)
        if not swapped:
            break
        swapped = False
        end -= 1
        for i in range(end - 1, start - 1, -1):
            profiler.op()
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
                profiler.op(3)
        start += 1
    profiler.finish()
    return a


ALGORITHMS = {
    '\nBubble Sort\n': bubble_sort,
    '\nSelection Sort\n': selection_sort,
    '\nInsertion Sort\n': insertion_sort,
    '\nShell Sort\n': shell_sort,
    '\nMerge Sort\n': merge_sort,
    '\nQuick Sort\n': quick_sort,
    '\nHeap Sort\n': heap_sort,
    '\nCounting Sort\n': counting_sort,
    '\nRadix Sort\n': radix_sort,
    '\nBucket Sort\n': bucket_sort,
    '\nCocktail Sort\n': cocktail_sort,
}

# --------------------------- Carga de datos --------------------------------

def cargar_datos(path=None):
    """Lee archivo .xlsx, .csv o .txt y devuelve un DataFrame con hasta MAX_RECORDS filas."""
    try:
        if path is None:
            path = filedialog.askopenfilename(title='Seleccionar archivo de datos',
                                              filetypes=[('Excel', '*.xlsx'), ('CSV', '*.csv'), ('Texto', '*.txt'), ('Todos', '*.*')])
            if not path:
                return None
        if path.lower().endswith('.xlsx'):
            df = pd.read_excel(path)
        elif path.lower().endswith('.csv'):
            df = pd.read_csv(path)
        else:
            # txt o genérico: intentar con pandas read_csv (delimitador autodetectado)
            df = pd.read_csv(path, sep=None, engine='python')
        # limitar a MAX_RECORDS
        if len(df) > MAX_RECORDS:
            registrar_log(f'Archivo {path} tiene {len(df)} registros; se truncará a {MAX_RECORDS}.')
            df = df.iloc[:MAX_RECORDS].copy()
        else:
            registrar_log(f'Archivo {path} cargado con {len(df)} registros.')
        return df
    except Exception as e:
        registrar_log('Error al cargar datos: ' + str(e))
        messagebox.showerror('Error', f'No se pudo cargar el archivo: {e}')
        return None


# --------------------------- Interfaz Gráfica -------------------------------

class SortingApp:
    def __init__(self, root):
        # Reiniciar archivo de LOG en cada inicio de programa
        try:
            with open(LOG_FILE, 'w', encoding='utf-8') as f:
                f.write("")  # Limpia el log para no arrastrar sesiones anteriores
        except:
            pass

        self.root = root
        self.root.title('Proyecto Ordenamiento - Equipo 14 \n- Héctor Jesús Valadez Pardo y Alberto Roman Campos')
        self.df_original = None  # DataFrame al cargar
        self.df_sorted = None    # DataFrame ordenado (si aplica)
        self.last_results = {}   # resultados por método
        self.current_column = None
        # Estadísticas de métodos: almacena tiempos (ns) por método para MO Alfa
        self.method_stats = {}
        # Indica si se ha guardado el reporte MO Alfa (evita sobrescribir accidentalmente)
        self._mo_alfa_guardado = False

        self._build_ui()
        self.cargar_excel_inicial()

    def action_explicaciones(self):
        """
        Muestra en una sola ventana las explicaciones de métodos de
        ordenamiento y búsqueda.
        """
        win = tk.Toplevel(self.root)
        win.title("Explicaciones de Ordenamiento y Búsqueda")
        win.geometry("680x620")

        texto = (
            "EXPLICACIÓN DE MÉTODOS DE ORDENAMIENTO\n\n"
            "• QuickSort: Método rápido basado en pivote y división.\n"
            "• MergeSort: Divide listas y las mezcla de manera ordenada.\n"
            "• HeapSort: Construye un montículo y extrae el mínimo/máximo.\n"
            "• RadixSort: Ordena por dígitos desde menor a mayor.\n"
            "• CountingSort: Cuenta ocurrencias, muy rápido en rangos pequeños.\n"
            "• BucketSort: Distribuye elementos en cubetas y luego ordena.\n"
            "• Burbuja / Selección / Inserción: Métodos simples O(n²).\n\n"
            "--------------------------------------------------------------\n\n"
            "EXPLICACIÓN DE MÉTODOS DE BÚSQUEDA\n\n"
            "• Secuencial:\n"
            "  Recorre los elementos uno por uno hasta encontrar el valor.\n\n"
            "• Binaria:\n"
            "  Solo funciona cuando los datos están ordenados.\n"
            "  Divide el conjunto por la mitad repetidamente.\n\n"
            "• Interpolación:\n"
            "  Calcula la posición estimada donde debería estar el valor.\n"
            "  Funciona mejor si los datos están uniformemente distribuidos.\n"
        )

        ttk.Label(win, text=texto, justify='left', wraplength=650).pack(padx=12, pady=10)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=10)

    def _build_ui(self):
        # Cabecera con información del equipo
        header = ttk.Frame(self.root, padding=8)
        header.pack(fill='x')
        ttk.Label(header, text=TEAM_INFO['equipo'], font=('Helvetica', 14, 'bold')).pack(anchor='w')
        ttk.Label(header, text=f"Tema: {TEAM_INFO['tema']}", font=('Helvetica', 10)).pack(anchor='w')
        ttk.Label(header, text=f"Integrantes: {', '.join(TEAM_INFO['integrantes'])}", font=('Helvetica', 10)).pack(anchor='w')

        # Controles principales
        ctrl = ttk.Frame(self.root, padding=8)
        ctrl.pack(fill='x')

        # ---------------- Tabla principal (Treeview) ----------------
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill='both', expand=True)

        self.tree = ttk.Treeview(main, columns=(), show='headings')
        self.tree_scroll = ttk.Scrollbar(main, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree_scroll.pack(side='left', fill='y')

        # Panel lateral para posibles gráficas o información
        right = ttk.Frame(main)
        right.pack(side='left', fill='both', expand=False)
        self.legend_var = tk.StringVar(value='')
        ttk.Label(right, textvariable=self.legend_var, wraplength=250).pack(pady=6)
        ttk.Button(ctrl, text='Mostrar', command=self.action_mostrar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Ordenar', command=self.action_ordenar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Buscar', command=self.action_buscar).pack(side='left', padx=4)
        # Botones adicionales de funcionalidad extra (Insertar, Reportes, MO Alfa, Ordenar Todo, Acerca de)
        ttk.Button(ctrl, text='Insertar', command=self.action_insertar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Reportes', command=self.action_reporte).pack(side='left', padx=4)
        ttk.Button(ctrl, text='MO Alfa', command=self.action_mo_alfa).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Acerca de', command=self.action_acerca_de).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Salir', command=self.root.quit).pack(side='right', padx=4)
    # ----------------- Funciones adicionales: Insertar, Reportes y MO Alfa -----------------
    def cargar_excel_inicial(self):
        """
        Carga automáticamente el archivo MOCK_DATA.xlsx al iniciar el programa.
        """
        ruta = r"/Users/hectorjesus/PycharmProjects/Metodos_Ordenacion_Proyecto/MOCK_DATA.xlsx"

        try:
            df = pd.read_excel(ruta)
            self.df_original = df.copy()
            self._refresh_tree(self.df_original)
            registrar_log(f"Archivo cargado automáticamente: {ruta}")
            messagebox.showinfo("Carga Automática", "Datos cargados correctamente al iniciar.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el archivo inicial:\n{e}")
            registrar_log("Error al cargar archivo inicial: " + str(e))


    def action_insertar(self):
        """
        Abre una ventana para insertar un nuevo registro, recoge valores de las columnas del DataFrame
        y los agrega como nueva fila.
        """
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        win = tk.Toplevel(self.root)
        win.title('Insertar nuevo registro')
        ttk.Label(win, text='Introduce los valores para cada columna:').pack(anchor='w', padx=6, pady=(6, 0))
        entries = {}
        for col in self.df_original.columns:
            ttk.Label(win, text=col).pack(anchor='w', padx=6)
            var = tk.StringVar()
            entry = ttk.Entry(win, textvariable=var)
            entry.pack(fill='x', padx=6, pady=2)
            entries[col] = var

        def agregar():
            nuevo = {col: entries[col].get() for col in self.df_original.columns}
            # Validación simple: no permitir todos vacíos
            if all(v.strip() == '' for v in nuevo.values()):
                messagebox.showwarning('Atención', 'No puede insertar una fila vacía.')
                return
            try:
                self.df_original.loc[len(self.df_original)] = nuevo
                self.df_original.reset_index(drop=True, inplace=True)
                self.df_sorted = None  # invalidar ordenado
                self._refresh_tree(self.df_original)
                registrar_log(f'Nuevo registro insertado: {nuevo}')
                messagebox.showinfo('Insertar', 'Registro insertado correctamente.')
                win.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo insertar el registro: {e}')
                registrar_log('Error al insertar registro: ' + str(e))

        ttk.Button(win, text='Agregar', command=agregar).pack(pady=6)
        ttk.Button(win, text='Cancelar', command=win.destroy).pack(pady=2)
        ttk.Button(win, text='Volver al menú', command=win.destroy).pack(pady=2)

    def action_reporte(self):
        """
        Genera reportes de ORDENAMIENTO y BÚSQUEDA.
        (MO Alfa ya no se usa)
        """
        # Ventana para seleccionar tipo de reporte
        win_tipo = tk.Toplevel(self.root)
        win_tipo.title("Seleccionar tipo de reporte")
        win_tipo.geometry("360x200")

        tk.Label(win_tipo, text="Selecciona el tipo de reporte:", font=("Arial", 12)).pack(pady=10)

        tipo_var = tk.StringVar()
        combo = ttk.Combobox(win_tipo, textvariable=tipo_var,
                             values=["Ordenamiento", "Búsqueda"],
                             state="readonly")
        combo.pack(pady=10)
        combo.current(0)

        def continuar():
            tipo = tipo_var.get()
            win_tipo.destroy()

            if tipo == "Ordenamiento":
                self._menu_reporte_ordenamiento()
            elif tipo == "Búsqueda":
                self._generar_reporte_busqueda()

        ttk.Button(win_tipo, text="Continuar", command=continuar).pack(pady=8)
        ttk.Button(win_tipo, text="Cancelar", command=win_tipo.destroy).pack()

    def _menu_reporte_ordenamiento(self):
        """
        Submenú para elegir campo clave y generar reporte de ordenamiento.
        Requiere que exista un ordenamiento previo.
        """

        if not hasattr(self, 'ultimo_ordenamiento') or self.ultimo_ordenamiento is None:
            messagebox.showerror("Error",
                                 "No se ha realizado ningún ordenamiento.\nOrdena un campo antes de generar el reporte.")
            return

        win = tk.Toplevel(self.root)
        win.title("Reporte de Ordenamiento")
        win.geometry("350x180")

        tk.Label(win, text="Selecciona el campo clave:", font=('Arial', 11)).pack(pady=10)

        columnas = list(self.df_original.columns)
        campo_var = tk.StringVar()
        combo = ttk.Combobox(win, textvariable=campo_var, values=columnas, state="readonly")
        combo.pack(pady=10)

        def generar():
            if campo_var.get() == "":
                messagebox.showerror("Error", "Debes seleccionar un campo clave.")
                return

            try:
                nombre = "REPORTE_ORDENAMIENTO.xlsx"

                df_resumen = pd.DataFrame([{
                    'Método': self.ultimo_ordenamiento['metodo'],
                    'Columna': campo_var.get(),
                    'Tiempo_ns': self.ultimo_ordenamiento['tiempo'],
                    'Registros': len(self.df_original)
                }])

                with pd.ExcelWriter(nombre, engine='openpyxl') as writer:
                    df_resumen.to_excel(writer, index=False, sheet_name='Resumen')
                    self.df_original.to_excel(writer, index=False, sheet_name='Datos_Ordenados')

                registrar_log(f"Reporte de ordenamiento generado: {nombre}")
                messagebox.showinfo("Reporte", f"Reporte generado correctamente:\n{nombre}")
                win.destroy()

            except Exception as e:
                registrar_log(f"ERROR reporte ordenamiento: {e}")
                messagebox.showerror("Error", f"No se pudo generar el reporte:\n{e}")

        ttk.Button(win, text="Generar", command=generar).pack(pady=8)
        ttk.Button(win, text="Cancelar", command=win.destroy).pack()

    def _generar_reporte_busqueda(self):
        """
        Genera reporte de búsquedas (solo esta sesión)
        con un SUBMENÚ que incluye CAMPOS CLAVE.
        """

        if not os.path.exists(LOG_FILE):
            messagebox.showwarning('Advertencia', 'No se encontró el archivo de log.')
            return

        # SUBMENÚ
        win = tk.Toplevel(self.root)
        win.title("Reporte de Búsqueda")
        win.geometry("380x260")

        ttk.Label(win, text="Generar reporte de búsquedas\n(sesión actual):",
                  font=("Arial", 11)).pack(pady=10)

        # Selección de campo clave
        ttk.Label(win, text="Selecciona el campo clave:", font=("Arial", 10)).pack(pady=4)

        columnas = list(self.df_original.columns)
        campo_var = tk.StringVar()
        combo_campos = ttk.Combobox(
            win, textvariable=campo_var,
            values=columnas, state="readonly"
        )
        combo_campos.pack(pady=6)

        ttk.Label(win, text="¿Qué deseas hacer?", font=("Arial", 10)).pack(pady=(12, 4))

        opcion = tk.StringVar()
        combo_accion = ttk.Combobox(
            win, textvariable=opcion,
            values=["Generar reporte", "Cancelar"],
            state="readonly"
        )
        combo_accion.pack(pady=6)
        combo_accion.current(0)

        def continuar():
            accion = opcion.get()
            campo = campo_var.get()

            if accion == "Cancelar":
                win.destroy()
                return

            if campo == "":
                messagebox.showerror("Error", "Debes seleccionar un campo clave para el reporte.")
                return

            win.destroy()

            try:
                # Leer log de la sesión
                with open(LOG_FILE, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Filtrar únicamente registros de búsqueda
                busquedas = [
                    line for line in lines
                    if ('Búsqueda' in line or 'búsqueda' in line)
                ]

                if not busquedas:
                    messagebox.showwarning(
                        'Advertencia',
                        'No se encontraron registros de búsqueda en esta sesión.'
                    )
                    return

                # Crear archivo
                nombre = "REPORTE_BUSQUEDAS.txt"

                with open(nombre, 'w', encoding='utf-8') as fout:
                    fout.write("===== REPORTE DE BÚSQUEDAS =====\n")
                    fout.write("Proyecto: Energía\n")
                    fout.write("Equipo 14 - Energía\n")
                    fout.write("Integrantes: Héctor Jesús Valadez Pardo, Alberto Roman Campos\n")
                    fout.write("----------------------------------------------\n\n")
                    fout.write(f"Campo clave seleccionado: {campo}\n\n")
                    fout.write("Registros:\n\n")
                    for b in busquedas:
                        fout.write(b)

                registrar_log(f"Reporte de búsquedas generado: {nombre}")
                messagebox.showinfo(
                    'Reporte',
                    f'Reporte generado correctamente:\n{nombre}'
                )

            except Exception as e:
                registrar_log("ERROR reporte búsqueda: " + str(e))
                messagebox.showerror(
                    "Error",
                    f"No se pudo generar el reporte de búsqueda:\n{e}"
                )

        ttk.Button(win, text="Continuar", command=continuar).pack(pady=10)
        ttk.Button(win, text="Cerrar", command=win.destroy).pack(pady=2)

    def action_acerca_de(self):
        """
        Ventana pequeña con información básica del proyecto.
        """
        win = tk.Toplevel(self.root)
        win.title('Acerca del Proyecto')
        win.geometry('360x220')

        texto = (
            f"Proyecto: {TEAM_INFO['tema']}\n"
            f"Equipo: {TEAM_INFO['equipo']}\n"
            f"Integrantes:\n- Héctor Jesús Valadez Pardo\n- Alberto Roman Campos\n\n"
            "Sistema para comparar 11 métodos de\n"
            "ordenamiento y búsquedas.\n"
        )

        ttk.Label(win, text=texto, justify='left').pack(padx=10, pady=10)
        ttk.Button(win, text='Cerrar', command=win.destroy).pack(pady=8)

    def action_campos_clave(self):
        """
        Muestra cuáles son los campos clave y complementarios (requerido por PDF).
        """
        win = tk.Toplevel(self.root)
        win.title("Campos Clave")
        win.geometry("360x260")

        texto = (
            "Campos clave para ordenamiento y búsqueda:\n\n"
            "ID_PLANTA\nFecha\nTipo de Fuente\nCapacidad\nUbicación\nProveedor Turbinas\nMantenimiento\n"
        )
        ttk.Label(win, text=texto, justify='left', wraplength=330).pack(padx=10, pady=10)
        ttk.Button(win, text='Volver al menú', command=win.destroy).pack(pady=6)


    def action_ordenar_todo(self):
        """
        Ordena todas las columnas del DataFrame usando Quick Sort por defecto y registra tiempos.
        """
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        try:
            resultados = []
            total_ns = 0
            for col in self.df_original.columns:
                series = self.df_original[col]
                # Preparar lista para ordenar (mismo proceso que action_ordenar)
                try:
                    serie_num = pd.to_numeric(series, errors='coerce', downcast='float')
                    if serie_num.isna().all():
                        data_list = series.astype(str).tolist()
                    else:
                        data_list = serie_num.fillna(method='ffill').tolist()
                except Exception:
                    data_list = series.astype(str).tolist()
                profiler = Profiler()
                start_ns = time.perf_counter_ns()
                sorted_vals = ALGORITHMS['\nQuick Sort\n'](data_list, profiler)
                end_ns = time.perf_counter_ns()
                elapsed = end_ns - start_ns
                resultados.append((col, elapsed))
                total_ns += elapsed
                # registrar estadística por método (Quick Sort)
                self.method_stats.setdefault('\nQuick Sort\n'.strip(), []).append(elapsed)
            resumen = '\n'.join([f"{c}: {t:,} ns" for c, t in resultados])
            messagebox.showinfo('Ordenar Todo', f'Se ordenaron {len(resultados)} columnas con Quick Sort.\nTiempo total: {total_ns:,} ns')
            registrar_log('Ordenar Todo: ' + resumen)
        except Exception as e:
            registrar_log('Error en action_ordenar_todo: ' + str(e) + '\n' + traceback.format_exc())
            messagebox.showerror('Error', f'Error al ordenar todas las columnas: {e}')

    def action_mo_alfa(self):
        """
        Genera automáticamente el reporte MO Alfa sin abrir ventanas.
        """
        # Inicializar estadísticas si no existen
        if not hasattr(self, 'method_stats'):
            self.method_stats = {}

        # Asegurar que existan todas las claves
        for metodo in ALGORITHMS.keys():
            if metodo.strip() not in self.method_stats:
                self.method_stats[metodo.strip()] = []

        # Preparar resumen
        resumen_datos = []
        for metodo, tiempos in self.method_stats.items():
            ejecuciones = len(tiempos)
            promedio = int(sum(tiempos) / ejecuciones) if ejecuciones > 0 else 0
            resumen_datos.append((metodo.strip(), ejecuciones, promedio))

        # Determinar mejor método
        metodos_con_datos = [x for x in resumen_datos if x[1] > 0]
        mejor = None
        if metodos_con_datos:
            mejor = min(metodos_con_datos, key=lambda x: x[2])

        # Nombre del archivo acumulado
        archivo_acumulado = "MO_ALFA_HISTORICO.xlsx"
        nombre_hoja = "MO_ALFA_" + datetime.now().strftime('%Y%m%d_%H%M%S')

        # Crear DataFrame
        resumen_df = pd.DataFrame([
            {'Método': m, 'Ejecuciones': e, 'Promedio_ns': p}
            for m, e, p in resumen_datos
        ])

        try:
            if os.path.exists(archivo_acumulado):
                with pd.ExcelWriter(archivo_acumulado, engine='openpyxl', mode='a', if_sheet_exists='new') as writer:
                    resumen_df.to_excel(writer, index=False, sheet_name=nombre_hoja)
                    if mejor:
                        pd.DataFrame([{
                            'MO_Alfa': mejor[0],
                            'Promedio_ns': mejor[2]
                        }]).to_excel(writer, index=False, sheet_name=nombre_hoja + "_MEJOR")
            else:
                with pd.ExcelWriter(archivo_acumulado, engine='openpyxl') as writer:
                    resumen_df.to_excel(writer, index=False, sheet_name=nombre_hoja)
                    if mejor:
                        pd.DataFrame([{
                            'MO_Alfa': mejor[0],
                            'Promedio_ns': mejor[2]
                        }]).to_excel(writer, index=False, sheet_name=nombre_hoja + "_MEJOR")

            registrar_log(f"Reporte automático MO Alfa generado: {archivo_acumulado}")
            messagebox.showinfo("MO Alfa", f"Reporte MO Alfa generado automáticamente:\n{archivo_acumulado}")

        except Exception as e:
            registrar_log(f"Error guardando reporte MO Alfa: {e}")
            messagebox.showerror("Error", f"No se pudo guardar el reporte MO Alfa:\n{e}")



    def action_cargar(self):
        df = cargar_datos()
        if df is None:
            return
        self.df_original = df.reset_index(drop=True)
        self.df_sorted = None
        self.current_column = None
        messagebox.showinfo('Datos cargados', f'Datos cargados correctamente ({len(self.df_original)} registros).')
        registrar_log(f'Datos cargados: {len(self.df_original)} registros.')
        self._refresh_tree(self.df_original)

    def action_mostrar(self):
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        # Dialogo para elegir ver original o ordenado
        choice = messagebox.askquestion('Mostrar', '¿Desea ver los datos ordenados? (Si = ordenados, No = originales)')
        if choice == 'yes' and self.df_sorted is not None:
            self._refresh_tree(self.df_sorted)
            registrar_log('Usuario solicitó visualizar datos ordenados.')
        else:
            self._refresh_tree(self.df_original)
            registrar_log('Usuario solicitó visualizar datos originales.')

    def action_buscar(self):
        """Abre ventana para buscar un registro (búsqueda secuencial o binaria)."""
        if self.df_original is None or self.df_original.empty:
            messagebox.showwarning("Advertencia", "Primero carga los datos antes de buscar.")
            return

        win = tk.Toplevel(self.root)
        win.title("Buscar registro")
        win.geometry("340x240")
        win.configure(bg="#222")

        ttk.Label(win, text="Selecciona columna:", background="#222", foreground="white").pack(pady=4)
        col_var = tk.StringVar(value=self.df_original.columns[0])
        ttk.Combobox(win, textvariable=col_var, values=list(self.df_original.columns)).pack(pady=3)

        ttk.Label(win, text="Valor a buscar:", background="#222", foreground="white").pack(pady=4)
        val_entry = ttk.Entry(win)
        val_entry.pack(pady=3)

        def busqueda_interpolacion(self, datos, valor):
            """
            Implementación de búsqueda por interpolación.
            Requiere que los datos sean numéricos y estén ordenados.
            """
            try:
                datos_float = [float(x) for x in datos]
            except:
                return None  # No se puede operar

            low, high = 0, len(datos_float) - 1

            while low <= high and datos_float[low] <= valor <= datos_float[high]:
                pos = low + int(
                    ((valor - datos_float[low]) * (high - low)) /
                    (datos_float[high] - datos_float[low] + 1e-9)
                )
                if datos_float[pos] == valor:
                    return pos
                if datos_float[pos] < valor:
                    low = pos + 1
                else:
                    high = pos - 1

            return None

        def ejecutar_busqueda():
            columna = col_var.get()
            valor = val_entry.get().strip()
            if not valor:
                messagebox.showwarning("Advertencia", "Introduce un valor para buscar.")
                return

            try:
                try:
                    valor = float(valor) if "." in valor else int(valor)
                except ValueError:
                    try:
                        valor = pd.to_datetime(valor, errors='raise')
                    except Exception:
                        pass

                # Elegir método: Binaria solo si la columna está ordenada
                df_ref = self.df_sorted if hasattr(self, 'df_sorted') and self.df_sorted is not None else self.df_original
                datos = df_ref[columna].tolist()
                esta_ordenada = datos == sorted(datos, key=lambda x: (str(type(x)), x))
                # Nuevo bloque para métodos disponibles y selección predeterminada
                metodos_disponibles = ["Secuencial"]
                if esta_ordenada:
                    metodos_disponibles.append("Binaria")
                    if not esta_ordenada and valor.replace('.', '', 1).isdigit():
                        messagebox.showwarning("Aviso", "Para realizar búsqueda BINARIA debes ordenar primero.")

                # Selección automática: si está ordenada → Binaria, si no → Secuencial
                metodo = "Binaria" if esta_ordenada else "Secuencial"

                encontrado = False
                indice = -1
                inicio = time.perf_counter_ns()

                if metodo == "Secuencial":
                    # Búsqueda secuencial mejorada con soporte para fechas y números
                    for i, v in enumerate(datos):
                        try:
                            # Intentar comparar como fecha
                            v_dt = pd.to_datetime(v, errors='coerce')
                            valor_dt = pd.to_datetime(valor, errors='coerce')
                            if not pd.isna(v_dt) and not pd.isna(valor_dt):
                                if v_dt == valor_dt:
                                    indice = i
                                    encontrado = True
                                    break
                        except:
                            pass

                        try:
                            # Intentar comparar como número
                            v_num = float(v)
                            valor_num = float(valor)
                            if v_num == valor_num:
                                indice = i
                                encontrado = True
                                break
                        except:
                            pass

                        # Comparación como texto
                        if str(v).lower().strip() == str(valor).lower().strip():
                            indice = i
                            encontrado = True
                            break
                elif metodo == "Binaria":
                    # Binaria preferente, pero si no es aplicable, usar secuencial
                    if all(isinstance(x, (int, float, pd.Timestamp)) for x in datos):
                        datos_convertidos = []
                        for x in datos:
                            if isinstance(x, pd.Timestamp):
                                datos_convertidos.append(x.timestamp())
                            elif isinstance(x, (int, float)):
                                datos_convertidos.append(float(x))
                            else:
                                datos_convertidos.append(float('inf'))

                        datos_ordenados = sorted(enumerate(datos_convertidos), key=lambda x: x[1])
                        indices, valores = zip(*datos_ordenados)
                        valor_num = valor.timestamp() if isinstance(valor, pd.Timestamp) else float(valor)
                        low, high = 0, len(valores) - 1
                        while low <= high:
                            mid = (low + high) // 2
                            if valores[mid] == valor_num:
                                indice = indices[mid]
                                encontrado = True
                                break
                            elif valores[mid] < valor_num:
                                low = mid + 1
                            else:
                                high = mid - 1
                    else:
                        for i, v in enumerate(datos):
                            if str(v).lower() == str(valor).lower():
                                indice = i
                                encontrado = True
                                break

                fin = time.perf_counter_ns()
                duracion = fin - inicio

                if encontrado:
                    resultado = df_ref.iloc[indice].to_dict()
                    resultado_txt = "\n".join([f"{k}: {v}" for k, v in resultado.items()])
                    messagebox.showinfo("Resultado",
                        f"Método usado: {metodo}\nDuración: {duracion} ns\n\nRegistro encontrado:\n\n{resultado_txt}")
                    win.destroy()
                else:
                    messagebox.showwarning("No encontrado",
                        f"El valor '{valor}' no se encontró en la columna '{columna}'.\nMétodo usado: {metodo}\nTiempo: {duracion} ns")
                    win.destroy()

                registrar_log(f"Búsqueda con {metodo} - Columna: {columna} - Valor: {valor} - Tiempo: {duracion} ns")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo realizar la búsqueda: {e}")
                registrar_log("Error en búsqueda: " + str(e))

        ttk.Button(win, text="Buscar", command=ejecutar_busqueda).pack(pady=6)
        ttk.Button(win, text="Volver al menú", command=win.destroy).pack(pady=3)


    def action_guardar(self):
        if self.df_sorted is None and self.df_original is None:
            messagebox.showwarning('Atención', 'No hay datos para guardar.')
            return
        try:
            target = self.df_sorted if self.df_sorted is not None else self.df_original
            path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
            if not path:
                return
            target.to_excel(path, index=False)
            messagebox.showinfo('Guardado', f'Archivo guardado en: {path}')
            registrar_log(f'Datos guardados en {path}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo: {e}')
            registrar_log('Error guardando archivo: ' + str(e))

    def action_ordenar(self):
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        # Submenú para elegir método
        win = tk.Toplevel(self.root)
        win.title('Ordenar datos')

        ttk.Label(win, text='Selecciona columna para ordenar:').pack(anchor='w', padx=6, pady=(6, 0))
        cols = list(self.df_original.columns)
        col_var = tk.StringVar()
        combo = ttk.Combobox(win, values=cols, state='readonly', textvariable=col_var)
        combo.pack(fill='x', padx=6, pady=4)
        if cols:
            combo.current(0)

        ttk.Label(win, text='Selecciona método:').pack(anchor='w', padx=6, pady=(6, 0))
        methods = ['Aleatorio', 'Avanzado', 'QuickSort (Rápido)', 'MergeSort (Mezcla)']
        method_var = tk.StringVar(value=methods[0])
        method_combo = ttk.Combobox(win, values=methods, state='readonly', textvariable=method_var)
        method_combo.pack(fill='x', padx=6, pady=4)

        # Si elige Avanzado, permitir seleccionar entre todos
        adv_var = tk.StringVar()
        adv_combo = ttk.Combobox(win, values=list(ALGORITHMS.keys()), state='readonly', textvariable=adv_var)



        def on_method_change(event=None):
            if method_var.get() == 'Avanzado':
                adv_combo.pack(fill='x', padx=6, pady=4)
                adv_combo.current(0)
            else:
                adv_combo.pack_forget()

        method_combo.bind('<<ComboboxSelected>>', on_method_change)

        def do_sort():
            col = col_var.get()
            method_choice = method_var.get()
            if method_choice == 'Avanzado':
                alg_key = adv_var.get()
            elif method_choice == 'QuickSort (Rápido)':
                alg_key = '\nQuick Sort\n'
            elif method_choice == 'MergeSort (Mezcla)':
                alg_key = '\nMerge Sort\n'
            elif method_choice == 'Aleatorio':
                alg_key = random.choice(list(ALGORITHMS.keys()))
            else:
                alg_key = '\nAleatorio\n'

            if not col:
                messagebox.showwarning('Atención', 'Selecciona una columna.')
                return

            # intentar convertir columna a numérica para ordenamiento estable si es posible
            series = self.df_original[col]
            try:
                serie_num = pd.to_numeric(series, errors='coerce', downcast='float')
                if serie_num.isna().all():
                    # no numéricos
                    data_list = series.astype(str).tolist()
                else:
                    data_list = serie_num.fillna(method='ffill').tolist()
            except Exception:
                data_list = series.astype(str).tolist()

            profiler = Profiler()
            start_ns = time.perf_counter_ns()
            try:
                # Ejecutar el algoritmo seleccionado y manejar posibles errores de recursión o tipo
                sorted_values = ALGORITHMS[alg_key](data_list, profiler)
            except RecursionError:
                messagebox.showerror(
                    'Error',
                    f'El método {alg_key} excedió la profundidad de recursión. Se usará MergeSort como respaldo.'
                )
                registrar_log(f'Fallo recursión en {alg_key}, se usó MergeSort en su lugar.')
                sorted_values = ALGORITHMS['\nMerge Sort\n'](data_list, profiler)
            except Exception as e:
                messagebox.showerror(
                    'Error',
                    f'No se pudo ordenar con {alg_key}: {e}\nSe usará MergeSort como respaldo.'
                )
                registrar_log('Error en ordenamiento: ' + str(e) + '\n' + traceback.format_exc())
                try:
                    sorted_values = ALGORITHMS['\nMerge Sort\n'](data_list, profiler)
                except Exception as e2:
                    messagebox.showerror(
                        'Error crítico',
                        f'Falló también el método de respaldo MergeSort: {e2}'
                    )
                    registrar_log('Error crítico en respaldo MergeSort: ' + str(e2))
                    return
            end_ns = time.perf_counter_ns()
            elapsed_ns = end_ns - start_ns

            # construir df_sorted reordenando filas completas basadas en la columna
            try:
                # crear mapping viejo->nuevo índice mediante argsort sobre sorted_values
                # para manejar filas completas, usar pandas merge approach
                temp_df = self.df_original.copy()
                temp_df['_sort_key_'] = series.astype(str) if isinstance(sorted_values[0], str) else pd.to_numeric(series, errors='coerce')
                # Crea un DataFrame con claves ordenadas
                sorted_df = pd.DataFrame({'_sort_key_': sorted_values})
                # Conservar duplicados añadiendo un índice auxiliar
                temp_df['_pos_'] = range(len(temp_df))
                sorted_df['_pos_'] = sorted_df.index
                # Realizaremos una unión estable: mapearemos las posiciones ordenando temp_df por _sort_key_ y luego tomando los N elementos superiores.
                try:
                    # Primero, ordena el original utilizando el algoritmo seleccionado en los valores clave para obtener los índices.
                    # Alternativa: usar pandas sort_values cuando la conversión a numérico sea exitosa.
                    if pd.api.types.is_numeric_dtype(temp_df['_sort_key_']):
                        idx_sorted = temp_df['_sort_key_'].argsort(kind='mergesort')
                    else:
                        idx_sorted = temp_df['_sort_key_'].astype(str).argsort(kind='mergesort')
                    df_result = temp_df.iloc[idx_sorted].drop(columns=['_sort_key_', '_pos_']).reset_index(drop=True)
                except Exception:
                    # alternativa: construir el resultado haciendo coincidir los elementos secuencialmente (maneja los duplicados de forma imperfecta).
                    res_rows = []
                    used = [False] * len(temp_df)
                    keys = temp_df[col].astype(str).tolist()
                    for val in sorted_values:
                        for i, k in enumerate(keys):
                            if not used[i] and str(k) == str(val):
                                res_rows.append(temp_df.iloc[i].drop(labels=['_sort_key_', '_pos_']))
                                used[i] = True
                                break
                    if res_rows:
                        df_result = pd.DataFrame(res_rows).reset_index(drop=True)
                    else:
                        df_result = temp_df.drop(columns=['_sort_key_', '_pos_']).reset_index(drop=True)
                self.df_sorted = df_result
                # Actualizar df_original con la versión ordenada
                self.df_original = self.df_sorted.copy()
            except Exception as e:
                # si falla la recomposición de filas, guardar al menos la columna ordenada
                registrar_log('Error reconstruyendo df_sorted: ' + str(e) + '\n' + traceback.format_exc())
                self.df_sorted = pd.DataFrame({col: sorted_values})
                # Actualizar df_original con la versión ordenada (aunque sea solo la columna)
                self.df_original = self.df_sorted.copy()

            # guardar resultados para graficar comparativo
            self.last_results = {
                'algorithm': alg_key,
                'elapsed_ns': elapsed_ns,
                'profiler_history': profiler.history
            }

            # Guardar estadísticas del método ejecutado para MO Alfa
            if not hasattr(self, 'method_stats'):
                self.method_stats = {}
            self.method_stats.setdefault(alg_key.strip(), []).append(elapsed_ns)

            # Registrar último ordenamiento para reportes
            self.ultimo_ordenamiento = {
                'metodo': alg_key.strip(),
                'columna': col,
                'tiempo': elapsed_ns
            }
            # mostrar leyenda (sin mostrar datos)
            self.legend_var.set(f'Ordenado por el método {alg_key} y se realizó en {elapsed_ns} nanosegundos')
            messagebox.showinfo('Ordenamiento completado', self.legend_var.get())
            registrar_log(f'Ordenado por {alg_key} en {elapsed_ns} ns')
            win.destroy()

        ttk.Button(win, text='Ordenar', command=do_sort).pack(pady=6)
        ttk.Button(win, text='Cancelar', command=win.destroy).pack(pady=2)

    # ----------------- Helpers -----------------------------------------------

    def _refresh_tree(self, df: pd.DataFrame):
        try:
            # limpiar tree
            for c in self.tree.get_children():
                self.tree.delete(c)
            self.tree['columns'] = list(df.columns)
            for col in df.columns:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=120, anchor='w')
            # insertar filas (solo hasta MAX_RECORDS para no bloquear la GUI)
            for i, row in df.reset_index(drop=True).iterrows():
                if i >= MAX_RECORDS:
                    break
                vals = [str(row[c]) for c in df.columns]
                self.tree.insert('', 'end', values=vals)
            registrar_log(f'Treeview actualizado con {min(len(df), MAX_RECORDS)} registros')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo mostrar la tabla: {e}')
            registrar_log('Error en _refresh_tree: ' + str(e) + '\n' + traceback.format_exc())


# --------------------------- Main -----------------------------------------

def main():
    """
    Función principal que inicia la aplicación de ordenamiento.
    """
    try:
        root = tk.Tk()
        app = SortingApp(root)
        root.geometry('1000x600')
        root.mainloop()
    except Exception as e:
        registrar_log('Error fatal en la aplicación: ' + str(e) + '\n' + traceback.format_exc())
        messagebox.showerror('Error fatal', f'La aplicación terminó por un error: {e}')


# --------------------------- Pantalla de Login -----------------------------
def pantalla_login():
    """
    Muestra una ventana de inicio de sesión con opción de registro.
    """
    import os
    USERS_FILE = "usuarios.txt"
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            f.write("admin,1234\n")

    def cargar_usuarios():
        usuarios = {}
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            for linea in f:
                if "," in linea:
                    u, c = linea.strip().split(",", 1)
                    usuarios[u] = c
        return usuarios

    def registrar_usuario():
        reg_win = tk.Toplevel(login_win)
        reg_win.title("Registrar nuevo usuario")
        reg_win.geometry("280x180")
        ttk.Label(reg_win, text="Nuevo usuario:").pack(pady=4)
        new_user = tk.StringVar()
        ttk.Entry(reg_win, textvariable=new_user).pack(pady=4)
        ttk.Label(reg_win, text="Contraseña:").pack(pady=4)
        new_pass = tk.StringVar()
        ttk.Entry(reg_win, textvariable=new_pass, show="*").pack(pady=4)

        def guardar_usuario():
            usuarios = cargar_usuarios()
            u, p = new_user.get().strip(), new_pass.get().strip()
            if not u or not p:
                messagebox.showwarning("Atención", "Completa ambos campos.")
                return
            if u in usuarios:
                messagebox.showwarning("Atención", "El usuario ya existe.")
                return
            with open(USERS_FILE, "a", encoding="utf-8") as f:
                f.write(f"{u},{p}\n")
            messagebox.showinfo("Registro", "Usuario registrado correctamente.")
            registrar_log(f"Nuevo usuario registrado: {u}")
            reg_win.destroy()

        ttk.Button(reg_win, text="Guardar", command=guardar_usuario).pack(pady=6)
        ttk.Button(reg_win, text="Cancelar", command=reg_win.destroy).pack(pady=2)

    login_win = tk.Tk()
    login_win.title("Inicio de sesión")
    login_win.geometry("320x200")
    login_win.resizable(False, False)
    # Centrar ventana si es posible
    try:
        login_win.eval('tk::PlaceWindow . center')
    except Exception:
        pass
    ttk.Label(login_win, text="Inicio de sesión", font=("Helvetica", 14, "bold")).pack(pady=10)
    frame = ttk.Frame(login_win, padding=10)
    frame.pack(fill="both", expand=True)
    ttk.Label(frame, text="Usuario:").grid(row=0, column=0, sticky="w", pady=4)
    user_var = tk.StringVar()
    ttk.Entry(frame, textvariable=user_var).grid(row=0, column=1, pady=4)
    ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, sticky="w", pady=4)
    pass_var = tk.StringVar()
    ttk.Entry(frame, textvariable=pass_var, show="*").grid(row=1, column=1, pady=4)

    def intentar_login():
        usuarios = cargar_usuarios()
        usuario, clave = user_var.get().strip(), pass_var.get().strip()
        if usuario in usuarios and usuarios[usuario] == clave:
            registrar_log(f"Login exitoso ({usuario})")
            login_win.destroy()
            main()
        else:
            registrar_log(f"Intento fallido de login: {usuario}")
            messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

    ttk.Button(frame, text="Ingresar", command=intentar_login).grid(row=2, column=0, pady=10)
    ttk.Button(frame, text="Registrar nuevo usuario", command=registrar_usuario).grid(row=2, column=1, pady=10)
    login_win.mainloop()


if __name__ == '__main__':
    # Ahora inicia mostrando la pantalla de login antes de la aplicación principal
    pantalla_login()
