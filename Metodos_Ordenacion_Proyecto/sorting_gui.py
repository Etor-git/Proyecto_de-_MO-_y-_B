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
        # Estadísticas de métodos: almacena tiempos (ns) por método para MO Alfa
        self.method_stats = {}
        # Indica si se ha guardado el reporte MO Alfa (evita sobrescribir accidentalmente)
        self._mo_alfa_guardado = False

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
        # Botones adicionales de funcionalidad extra (Insertar, Reportes, MO Alfa, Ordenar Todo, Acerca de)
        ttk.Button(ctrl, text='Insertar', command=self.action_insertar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Reportes', command=self.action_reporte).pack(side='left', padx=4)
        ttk.Button(ctrl, text='MO Alfa', command=self.action_mo_alfa).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Ordenar Todo', command=self.action_ordenar_todo).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Acerca de', command=self.action_acerca_de).pack(side='left', padx=4)
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
        ttk.Button(win, text='Volver al menú', command=win.destroy).pack(pady=2)

    def action_reporte(self):
        """Genera un reporte en formato .xlsx o .txt con estadísticas de métodos, búsquedas o MO Alfa."""
        if self.df_original is None or self.df_original.empty:
            messagebox.showwarning("Advertencia", "No hay datos cargados para generar reporte.")
            return

        win = tk.Toplevel(self.root)
        win.title("Generar reporte")
        win.geometry("330x320")
        win.configure(bg="#222")

        # Selección de tipo de reporte
        ttk.Label(win, text="Selecciona tipo de reporte:", background="#222", foreground="white").pack(pady=(8, 3))
        tipo_reporte_var = tk.StringVar(value='Ordenamiento')
        ttk.Radiobutton(win, text='Ordenamiento', variable=tipo_reporte_var, value='Ordenamiento').pack(pady=2)
        ttk.Radiobutton(win, text='Búsqueda', variable=tipo_reporte_var, value='Búsqueda').pack(pady=2)
        ttk.Radiobutton(win, text='MO Alfa', variable=tipo_reporte_var, value='MO Alfa').pack(pady=2)

        ttk.Label(win, text="Selecciona formato:", background="#222", foreground="white").pack(pady=10)
        formato_var = tk.StringVar(value='xlsx')
        ttk.Radiobutton(win, text='Excel (.xlsx)', variable=formato_var, value='xlsx').pack(pady=3)
        ttk.Radiobutton(win, text='Texto (.txt)', variable=formato_var, value='txt').pack(pady=3)

        def generar():
            formato = formato_var.get()
            tipo_reporte = tipo_reporte_var.get()
            if tipo_reporte == 'Ordenamiento':
                # Reporte de métodos de ordenamiento (como antes)
                if formato == 'xlsx':
                    path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
                    if not path:
                        return
                    try:
                        resumen_df = pd.DataFrame({
                            'Método': [], 'Ejecuciones': [], 'Promedio_ns': []
                        })
                        if hasattr(self, 'method_stats') and self.method_stats:
                            resumen_df = pd.DataFrame([
                                {'Método': m, 'Ejecuciones': len(v), 'Promedio_ns': (sum(v)//len(v) if len(v)>0 else 0)}
                                for m, v in self.method_stats.items()
                            ])
                        mo_rows = []
                        if not resumen_df.empty:
                            mejor = resumen_df.loc[resumen_df['Promedio_ns']>0].sort_values('Promedio_ns').head(1)
                            if not mejor.empty:
                                mo_rows = [{'MO_Alfa': mejor.iloc[0]['Método'], 'Promedio_ns': int(mejor.iloc[0]['Promedio_ns'])}]
                        with pd.ExcelWriter(path, engine='openpyxl') as writer:
                            self.df_original.to_excel(writer, index=False, sheet_name='Datos')
                            resumen_df.to_excel(writer, index=False, sheet_name='Resumen_Metodos')
                            pd.DataFrame(mo_rows).to_excel(writer, index=False, sheet_name='MO_Alfa')
                        registrar_log(f'Reporte (xlsx) generado en {path}')
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
                        # Guardar los datos originales y resumen de métodos en texto
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write("Datos:\n")
                            self.df_original.to_csv(f, index=False, sep='\t')
                            f.write("\nResumen de métodos:\n")
                            if hasattr(self, 'method_stats') and self.method_stats:
                                for m, v in self.method_stats.items():
                                    promedio = (sum(v)//len(v) if len(v)>0 else 0)
                                    f.write(f"{m}: {len(v)} ejecuciones, promedio {promedio:,} ns\n")
                        registrar_log(f'Reporte generado en {path}')
                        messagebox.showinfo('Reporte', f'Reporte generado en: {path}')
                        win.destroy()
                    except Exception as e:
                        messagebox.showerror('Error', f'No se pudo generar el reporte: {e}')
                        registrar_log('Error al generar reporte txt: ' + str(e))
            elif tipo_reporte == 'Búsqueda':
                # Reporte solo de búsquedas del log
                import os
                if not os.path.exists(LOG_FILE):
                    messagebox.showwarning('Advertencia', 'No se encontró el archivo de log.')
                    return
                try:
                    with open(LOG_FILE, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    # Filtrar solo líneas que sean de búsquedas
                    busquedas = [line for line in lines if 'Búsqueda' in line or 'búsqueda' in line]
                    if not busquedas:
                        messagebox.showwarning('Advertencia', 'No se encontraron registros de búsqueda en el log.')
                        return
                    if formato == 'xlsx':
                        path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
                        if not path:
                            return
                        # Guardar las búsquedas en un DataFrame
                        df_busq = pd.DataFrame({'Búsquedas': [b.strip() for b in busquedas]})
                        with pd.ExcelWriter(path, engine='openpyxl') as writer:
                            df_busq.to_excel(writer, index=False, sheet_name='Busquedas')
                        registrar_log(f'Reporte de búsquedas (xlsx) generado en {path}')
                        messagebox.showinfo('Reporte', f'Reporte de búsquedas generado en: {path}')
                        win.destroy()
                    else:
                        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Texto', '*.txt')])
                        if not path:
                            return
                        with open(path, 'w', encoding='utf-8') as fout:
                            fout.write("Registros de Búsqueda:\n")
                            for b in busquedas:
                                fout.write(b)
                        registrar_log(f'Reporte de búsquedas (txt) generado en {path}')
                        messagebox.showinfo('Reporte', f'Reporte de búsquedas generado en: {path}')
                        win.destroy()
                except Exception as e:
                    messagebox.showerror('Error', f'No se pudo generar el reporte de búsquedas: {e}')
                    registrar_log('Error al generar reporte de búsquedas: ' + str(e))
            elif tipo_reporte == 'MO Alfa':
                # Solo el análisis del mejor método (como bloque mo_rows)
                if formato == 'xlsx':
                    path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel', '*.xlsx')])
                    if not path:
                        return
                    try:
                        resumen_df = pd.DataFrame([
                            {'Método': m, 'Ejecuciones': len(v), 'Promedio_ns': (sum(v)//len(v) if len(v)>0 else 0)}
                            for m, v in self.method_stats.items()
                        ]) if hasattr(self, 'method_stats') and self.method_stats else pd.DataFrame()
                        mo_rows = []
                        if not resumen_df.empty:
                            mejor = resumen_df.loc[resumen_df['Promedio_ns']>0].sort_values('Promedio_ns').head(1)
                            if not mejor.empty:
                                mo_rows = [{'MO_Alfa': mejor.iloc[0]['Método'], 'Promedio_ns': int(mejor.iloc[0]['Promedio_ns'])}]
                        with pd.ExcelWriter(path, engine='openpyxl') as writer:
                            pd.DataFrame(mo_rows).to_excel(writer, index=False, sheet_name='MO_Alfa')
                        registrar_log(f'Reporte MO Alfa (xlsx) generado en {path}')
                        messagebox.showinfo('Reporte', f'Reporte MO Alfa generado en: {path}')
                        win.destroy()
                    except Exception as e:
                        messagebox.showerror('Error', f'No se pudo generar el reporte MO Alfa: {e}')
                        registrar_log('Error al generar reporte MO Alfa xlsx: ' + str(e))
                else:
                    path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Texto', '*.txt')])
                    if not path:
                        return
                    try:
                        resumen_df = pd.DataFrame([
                            {'Método': m, 'Ejecuciones': len(v), 'Promedio_ns': (sum(v)//len(v) if len(v)>0 else 0)}
                            for m, v in self.method_stats.items()
                        ]) if hasattr(self, 'method_stats') and self.method_stats else pd.DataFrame()
                        mo_txt = ""
                        if not resumen_df.empty:
                            mejor = resumen_df.loc[resumen_df['Promedio_ns']>0].sort_values('Promedio_ns').head(1)
                            if not mejor.empty:
                                mo_txt = f"MO_Alfa: {mejor.iloc[0]['Método']}, Promedio_ns: {int(mejor.iloc[0]['Promedio_ns'])}\n"
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write("Reporte MO Alfa\n")
                            f.write(mo_txt)
                        registrar_log(f'Reporte MO Alfa (txt) generado en {path}')
                        messagebox.showinfo('Reporte', f'Reporte MO Alfa generado en: {path}')
                        win.destroy()
                    except Exception as e:
                        messagebox.showerror('Error', f'No se pudo generar el reporte MO Alfa: {e}')
                        registrar_log('Error al generar reporte MO Alfa txt: ' + str(e))

        ttk.Button(win, text='Generar', command=generar).pack(pady=10)
        ttk.Button(win, text='Cancelar', command=win.destroy).pack(pady=2)

    def action_acerca_de(self):
        """
        Muestra información del proyecto (SADCE, equipo, integrantes, objetivo y lista de campos clave).
        """
        try:
            win = tk.Toplevel(self.root)
            win.title('Acerca del Proyecto')
            win.geometry('560x360')
            txt = (
                f"Proyecto: {TEAM_INFO['tema']}\n"
                f"Equipo: {TEAM_INFO['equipo']}\n"
                f"Integrantes: {', '.join(TEAM_INFO['integrantes'])}\n\n"
                "Descripción:\n"
                "Aplicación para comparar y analizar 11 métodos de ordenamiento sobre datos tabulares.\n"
                "Permite carga de archivos (.xlsx, .csv, .txt), inserción, búsqueda, reportes y generación de MO Alfa.\n\n"
                "Campos clave: ID_PLANTA, Tipo de Fuente, Fecha (u otras columnas temporales).\n"
            )
            lbl = ttk.Label(win, text=txt, justify='left', wraplength=520)
            lbl.pack(padx=10, pady=10)
            ttk.Button(win, text='Cerrar', command=win.destroy).pack(pady=8)
        except Exception as e:
            registrar_log('Error en action_acerca_de: ' + str(e))

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
        Analiza el rendimiento de los métodos ejecutados, muestra cuáles se repiten más,
        genera una tabla con los 11 métodos (aunque no se hayan usado) y guarda los resultados en el log.
        """
        # Inicializar estadísticas si no existen
        if not hasattr(self, 'method_stats'):
            self.method_stats = {}

        # Asegurar que existan las 11 claves en method_stats (aunque sin datos)
        for metodo in ALGORITHMS.keys():
            if metodo.strip() not in self.method_stats:
                self.method_stats[metodo.strip()] = []

        # Crear ventana principal
        win = tk.Toplevel(self.root)
        win.title('MO Alfa - Análisis de Métodos')
        win.geometry('950x650')

        ttk.Label(win, text='Análisis de Métodos de Ordenamiento (MO Alfa)', font=('Helvetica', 13, 'bold')).pack(pady=10)

        # Calcular promedios y repeticiones
        resumen_texto = ""
        resumen_datos = []
        for metodo, tiempos in self.method_stats.items():
            ejecuciones = len(tiempos)
            promedio = int(sum(tiempos) / ejecuciones) if ejecuciones > 0 else 0
            resumen_datos.append((metodo.strip(), ejecuciones, promedio))
            if ejecuciones > 0:
                resumen_texto += f"{metodo.strip()}: {ejecuciones} ejecuciones, promedio {promedio:,} ns\n"
            else:
                resumen_texto += f"{metodo.strip()}: Sin ejecuciones registradas\n"

        # Determinar el método más eficiente
        metodos_con_datos = [x for x in resumen_datos if x[1] > 0]
        if metodos_con_datos:
            mejor = min(metodos_con_datos, key=lambda x: x[2])
            resumen_texto += f"\nMétodo más eficiente: {mejor[0]} con {mejor[2]:,} ns (promedio)\n"
        else:
            mejor = None
            resumen_texto += "\nNo hay métodos ejecutados para calcular MO Alfa.\n"

        # Identificar métodos que se repiten más
        if metodos_con_datos:
            max_repe = max(metodos_con_datos, key=lambda x: x[1])[1]
            metodos_repetidos = [m for m, e, _ in resumen_datos if e == max_repe]
            resumen_texto += f"\nMétodos que se repiten más: {', '.join(metodos_repetidos)} ({max_repe} veces)\n"

        ttk.Label(win, text=resumen_texto, justify='left', wraplength=850).pack(pady=10)

        # Crear tabla con todos los métodos
        frame_tabla = ttk.Frame(win)
        frame_tabla.pack(fill='both', expand=True, padx=10, pady=10)
        columnas = ('Método', 'Ejecuciones', 'Promedio (ns)')
        tabla = ttk.Treeview(frame_tabla, columns=columnas, show='headings', height=12)
        for col in columnas:
            tabla.heading(col, text=col)
            tabla.column(col, anchor='center', width=250)
        for fila in resumen_datos:
            tabla.insert('', 'end', values=fila)
        tabla.pack(fill='both', expand=True)

        # Mostrar gráfico de rendimiento comparativo (solo métodos con datos)
        if metodos_con_datos:
            fig, ax = plt.subplots(figsize=(8, 4))
            metodos = [x[0] for x in metodos_con_datos]
            tiempos_prom = [x[2] for x in metodos_con_datos]
            ax.barh(metodos, tiempos_prom)
            ax.set_xlabel('Tiempo promedio (ns)')
            ax.set_title('Comparativa de rendimiento por método (el menos eficaz es el mas largo y el más eficiente es el mas largo)')
            ax.grid(True, axis='x')
            canvas = FigureCanvasTkAgg(fig, master=win)
            canvas.draw()
            canvas.get_tk_widget().pack(fill='both', expand=True, pady=10)

        # Guardar resultados MO Alfa en archivo de registro
        registrar_log("\n--- [MO Alfa] Análisis completo ---\n" + resumen_texto)
        for m, e, p in resumen_datos:
            registrar_log(f"{m}: {e} ejecuciones, promedio {p:,} ns")

        ttk.Button(win, text='Volver al menú', command=win.destroy).pack(pady=8)



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
                metodo = "Binaria" if esta_ordenada else "Secuencial"

                encontrado = False
                indice = -1
                inicio = time.perf_counter_ns()

                if metodo == "Binaria" and all(isinstance(x, (int, float, pd.Timestamp)) for x in datos):
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
