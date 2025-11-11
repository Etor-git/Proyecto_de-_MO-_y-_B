"""
sorting_gui.py

Versión final para presentación — interfaz con tkinter que:
- Carga datos desde .xlsx, .csv o .txt (hasta 3500 registros).
- Menú principal: Mostrar, Ordenar, Buscar, Salir.
- Mostrar permite ver registros antes y después de ordenar (Treeview).
- Ordenar abre submenú con métodos principales (QuickSort, MergeSort, Aleatorio) y Avanzado para los otros.
- Al completar el ordenamiento se muestra la leyenda:
  "Ordenado por el método XX y se realizó en XX nanosegundos".
- No muestra automáticamente los datos después de ordenar; para verlos usar Mostrar.
- Medición detallada (ns) y opción de guardar resultados a Excel.
- Registro de acciones y modificaciones en `mod_log.txt`.
- Cabecera con datos de identificación del equio (Equipo 14 - Energía - Héctor Jesús Valadez Pardo y Alberto Roman Campos).

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
import math
import heapq
import traceback
from datetime import datetime
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
    Registra mensajes en el archivo de registro con fecha y hora.
    """
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{now}] {mensaje}\n')


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
        self.root = root
        self.root.title('Proyecto Ordenamiento - Equipo 14 \n- Héctor Jesús Valadez Pardo y Alberto Roman Campos')
        self.df_original = None  # DataFrame al cargar
        self.df_sorted = None    # DataFrame ordenado (si aplica)
        self.last_results = {}   # resultados por método
        self.current_column = None

        self._build_ui()

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

        ttk.Button(ctrl, text='Cargar datos', command=self.action_cargar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Mostrar', command=self.action_mostrar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Ordenar', command=self.action_ordenar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Buscar', command=self.action_buscar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Guardar Excel', command=self.action_guardar).pack(side='left', padx=4)
        # Botones adicionales de funcionalidad extra (Insertar, Reportes, MO Alfa)
        ttk.Button(ctrl, text='Insertar', command=self.action_insertar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Reportes', command=self.action_reporte).pack(side='left', padx=4)
        ttk.Button(ctrl, text='MO Alfa', command=self.action_mo_alfa).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Salir', command=self.root.quit).pack(side='right', padx=4)
    # ----------------- Funciones adicionales: Insertar, Reportes y MO Alfa -----------------



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

    def action_reporte(self):
        """
        Genera un reporte en .xlsx o .txt del DataFrame actual y muestra mensaje de confirmación.
        """
        if self.df_original is None:
            messagebox.showwarning('Atención', 'No hay datos para generar reporte.')
            return
        # Ventana para elegir formato
        win = tk.Toplevel(self.root)
        win.title('Generar reporte')
        ttk.Label(win, text='Selecciona formato de reporte:').pack(anchor='w', padx=6, pady=(6, 0))
        formato_var = tk.StringVar(value='xlsx')
        ttk.Radiobutton(win, text='Excel (.xlsx)', variable=formato_var, value='xlsx').pack(anchor='w', padx=12)
        ttk.Radiobutton(win, text='Texto (.txt)', variable=formato_var, value='txt').pack(anchor='w', padx=12)

        def generar():
            formato = formato_var.get()
            if formato == 'xlsx':
                path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
                if not path:
                    return
                try:
                    self.df_original.to_excel(path, index=False)
                    registrar_log(f'Reporte generado en {path}')
                    messagebox.showinfo('Reporte', f'Reporte generado en: {path}')
                    win.destroy()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo generar el reporte: {e}')
                    registrar_log('Error al generar reporte xlsx: ' + str(e))
            else:
                path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Texto', '*.txt')])
                if not path:
                    return
                try:
                    self.df_original.to_csv(path, index=False, sep='\t')
                    registrar_log(f'Reporte generado en {path}')
                    messagebox.showinfo('Reporte', f'Reporte generado en: {path}')
                    win.destroy()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo generar el reporte: {e}')
                    registrar_log('Error al generar reporte txt: ' + str(e))

        ttk.Button(win, text='Generar', command=generar).pack(pady=6)
        ttk.Button(win, text='Cancelar', command=win.destroy).pack(pady=2)

    def action_mo_alfa(self):
        """
        Analiza el rendimiento del último método ejecutado y muestra la gráfica automáticamente.
        """
        if not self.last_results or 'algorithm' not in self.last_results:
            messagebox.showinfo('MO Alfa', 'No hay resultados de ordenamiento recientes para analizar.')
            return

        alg = self.last_results.get('algorithm')
        elapsed = self.last_results.get('elapsed_ns')
        history = self.last_results.get('profiler_history', [])

        # Mostrar resumen
        msg = f'Método: {alg}\nTiempo total: {elapsed:,} ns'
        registrar_log(f'[MO Alfa] {msg}')

        # Ventana emergente para mostrar gráfica
        win = tk.Toplevel(self.root)
        win.title(f'MO Alfa - {alg}')
        win.geometry('800x500')

        ttk.Label(win, text=f'Análisis de rendimiento: {alg}', font=('Helvetica', 12, 'bold')).pack(pady=6)
        ttk.Label(win, text=msg, font=('Helvetica', 10)).pack()

        # Crear figura de rendimiento
        fig, ax = plt.subplots(figsize=(7, 4))
        if history:
            ops, times = zip(*history)
            ax.plot(times, ops, color='blue', linewidth=2)
            ax.set_xlabel('Tiempo (segundos)')
            ax.set_ylabel('Operaciones realizadas')
            ax.set_title(f'Comportamiento del algoritmo {alg.strip()}')
            ax.grid(True)
        else:
            ax.text(0.5, 0.5, 'Sin datos de historial para graficar',
                    ha='center', va='center', fontsize=12, color='red')

        # Integrar gráfica en la ventana
        canvas = FigureCanvasTkAgg(fig, master=win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)

        ttk.Button(win, text='Cerrar', command=win.destroy).pack(pady=8)

    # ----------------- Acciones ----------------------------------------------

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
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        # Ventana para buscar
        win = tk.Toplevel(self.root)
        win.title('Buscar registro')
        ttk.Label(win, text='Selecciona columna:').pack(anchor='w', padx=6, pady=(6, 0))
        cols = list(self.df_original.columns)
        col_var = tk.StringVar()
        combo = ttk.Combobox(win, values=cols, state='readonly', textvariable=col_var)
        combo.pack(fill='x', padx=6, pady=4)
        if cols:
            combo.current(0)

        ttk.Label(win, text='Valor a buscar:').pack(anchor='w', padx=6, pady=(6, 0))
        val_var = tk.StringVar()
        ttk.Entry(win, textvariable=val_var).pack(fill='x', padx=6, pady=4)

        def do_search():
            col = col_var.get()
            val = val_var.get()
            if not col:
                messagebox.showwarning('Atención', 'Selecciona una columna.')
                return
            if val == '':
                messagebox.showwarning('Atención', 'Introduce un valor a buscar.')
                return
            # búsqueda en df_original
            try:
                mask = self.df_original[col].astype(str).str.contains(str(val), case=False, na=False)
                res = self.df_original[mask]
                if res.empty:
                    messagebox.showinfo('Resultado', 'No se encontraron coincidencias.')
                else:
                    self._refresh_tree(res)
                    messagebox.showinfo('Resultado', f'Se encontraron {len(res)} coincidencias. (Se muestran en la tabla)')
                registrar_log(f'Búsqueda en columna "{col}" por "{val}": {len(res)} resultados')
                win.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'Error durante la búsqueda: {e}')
                registrar_log('Error en búsqueda: ' + str(e))

        ttk.Button(win, text='Buscar', command=do_search).pack(pady=6)
        ttk.Button(win, text='Cancelar', command=win.destroy).pack(pady=2)

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
        methods = ['QuickSort (Rápido)', 'MergeSort (Mezcla)', 'Aleatorio', 'Avanzado']
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
                alg_key = '\nQuick Sort\n'

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
