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
- Cabecera con datos de identificación del equipo (Equipo 14 - Energía - Héctor Jesús Valadez Pardo y Alberto Roman Campos).

Dependencias:
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
MAX_RECORDS = 3500
TEAM_INFO = {
    'Equipo': 'Equipo 14 - Energía',
    'Integrantes': ['Héctor Jesús Valadez Pardo y Alberto Roman Campos'],
    'Materia': 'Métodos de Ordenación y Búsqueda'
}

# --------------------------- Utilidades -----------------------------------

def log(msg: str):
    """Registra mensajes en el archivo de log con fecha y hora."""
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'[{now}] {msg}\n')


# --------------------------- Instrumentación -------------------------------
class Profiler:
    def __init__(self):
        self.ops = 0
        self.history = []  # list of (ops, elapsed_seconds)
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
# Each algorithm takes (arr, profiler) and returns a sorted list (not in-place unless documented)

def bubble_sort(arr, profiler: Profiler):
    a = arr.copy()
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


def selection_sort(arr, profiler: Profiler):
    a = arr.copy()
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


def insertion_sort(arr, profiler: Profiler):
    a = arr.copy()
    profiler.start_timing()
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0:
            profiler.op()
            if a[j] > key:
                a[j + 1] = a[j]
                profiler.op(2)
                j -= 1
            else:
                break
        a[j + 1] = key
        profiler.op()
    profiler.finish()
    return a


def shell_sort(arr, profiler: Profiler):
    a = arr.copy()
    n = len(a)
    gap = n // 2
    profiler.start_timing()
    while gap > 0:
        for i in range(gap, n):
            temp = a[i]
            j = i
            while j >= gap:
                profiler.op()
                if a[j - gap] > temp:
                    a[j] = a[j - gap]
                    profiler.op(2)
                    j -= gap
                else:
                    break
            a[j] = temp
            profiler.op()
        gap //= 2
    profiler.finish()
    return a


def merge_sort(arr, profiler: Profiler):
    a = arr.copy()
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
            profiler.op()
        merged.extend(left[i:])
        merged.extend(right[j:])
        profiler.op(len(left) - i + len(right) - j)
        return merged

    res = merge(a)
    profiler.finish()
    return res


def quick_sort(arr, profiler: Profiler):
    a = arr.copy()
    profiler.start_timing()

    def quick(l, low, high):
        if low < high:
            p = partition(l, low, high)
            quick(l, low, p - 1)
            quick(l, p + 1, high)

    def partition(l, low, high):
        pivot_index = random.randint(low, high)
        l[pivot_index], l[high] = l[high], l[pivot_index]
        pivot = l[high]
        i = low
        for j in range(low, high):
            profiler.op()
            if l[j] < pivot:
                l[i], l[j] = l[j], l[i]
                profiler.op(3)
                i += 1
        l[i], l[high] = l[high], l[i]
        profiler.op(3)
        return i

    quick(a, 0, len(a) - 1)
    profiler.finish()
    return a


def heap_sort(arr, profiler: Profiler):
    a = arr.copy()
    profiler.start_timing()
    heap = []
    for x in a:
        heapq.heappush(heap, x)
        profiler.op()
    res = [heapq.heappop(heap) for _ in range(len(heap))]
    profiler.op(len(a))
    profiler.finish()
    return res


def counting_sort(arr, profiler: Profiler):
    a = list(arr)
    profiler.start_timing()
    if not all(isinstance(x, int) for x in a):
        raise ValueError('Counting Sort requires integer values.')
    if not a:
        profiler.finish()
        return []
    mn = min(a)
    mx = max(a)
    rng = mx - mn + 1
    if rng > 10_000_000:
        raise ValueError('Range too large for Counting Sort.')
    count = [0] * rng
    for v in a:
        count[v - mn] += 1
        profiler.op()
    res = []
    for i, c in enumerate(count):
        if c:
            res.extend([i + mn] * c)
            profiler.op(c)
    profiler.finish()
    return res


def radix_sort(arr, profiler: Profiler):
    a = list(arr)
    profiler.start_timing()
    if not all(isinstance(x, int) and x >= 0 for x in a):
        raise ValueError('Radix Sort expects non-negative integers.')
    if not a:
        profiler.finish()
        return []
    maxv = max(a)
    exp = 1
    while maxv // exp > 0:
        buckets = [[] for _ in range(10)]
        for num in a:
            buckets[(num // exp) % 10].append(num)
            profiler.op()
        a = [num for bucket in buckets for num in bucket]
        exp *= 10
        profiler.op()
    profiler.finish()
    return a


def bucket_sort(arr, profiler: Profiler):
    a = list(arr)
    profiler.start_timing()
    if not a:
        profiler.finish()
        return []
    mn, mx = min(a), max(a)
    if mn == mx:
        profiler.finish()
        return a.copy()
    n = len(a)
    buckets = [[] for _ in range(n)]
    for x in a:
        idx = int((x - mn) / (mx - mn) * (n - 1))
        buckets[idx].append(x)
        profiler.op()
    res = []
    for b in buckets:
        for x in b:
            res.append(x)
            j = len(res) - 2
            while j >= 0 and res[j] > res[j + 1]:
                res[j], res[j + 1] = res[j + 1], res[j]
                profiler.op(2)
                j -= 1
    profiler.finish()
    return res


def binary_insertion_sort(arr, profiler: Profiler):
    a = arr.copy()
    profiler.start_timing()
    for i in range(1, len(a)):
        key = a[i]
        lo, hi = 0, i
        while lo < hi:
            mid = (lo + hi) // 2
            profiler.op()
            if a[mid] <= key:
                lo = mid + 1
            else:
                hi = mid
        j = i
        while j > lo:
            a[j] = a[j - 1]
            profiler.op(2)
            j -= 1
        a[lo] = key
        profiler.op()
    profiler.finish()
    return a


ALGORITHMS = {
    'Burbuja': bubble_sort,
    'Seleccion': selection_sort,
    'Insercion': insertion_sort,
    'ShellSort': shell_sort,
    'MergeSort': merge_sort,
    'QuickSort': quick_sort,
    'HeapSort': heap_sort,
    'CountingSort': counting_sort,
    'RadixSort': radix_sort,
    'BucketSort': bucket_sort,
    'InsercionBinaria': binary_insertion_sort,
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
            log(f'Archivo {path} tiene {len(df)} registros; se truncará a {MAX_RECORDS}.')
            df = df.iloc[:MAX_RECORDS].copy()
        else:
            log(f'Archivo {path} cargado con {len(df)} registros.')
        return df
    except Exception as e:
        log('Error al cargar datos: ' + str(e))
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

        ttk.Button(ctrl, text='Cargar datos', command=self.action_cargar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Mostrar', command=self.action_mostrar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Ordenar', command=self.action_ordenar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Buscar', command=self.action_buscar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Guardar Excel', command=self.action_guardar).pack(side='left', padx=4)
        ttk.Button(ctrl, text='Salir', command=self.root.quit).pack(side='right', padx=4)

        # Área principal para tabla y gráfica
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill='both', expand=True)

        # Treeview para mostrar registros
        self.tree = ttk.Treeview(main, columns=(), show='headings')
        self.tree_scroll = ttk.Scrollbar(main, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.tree_scroll.set)
        self.tree.pack(side='left', fill='both', expand=True)
        self.tree_scroll.pack(side='left', fill='y')

        # Panel para gráficas y leyenda
        right = ttk.Frame(main)
        right.pack(side='left', fill='both', expand=False)

        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

        self.legend_var = tk.StringVar(value='')
        ttk.Label(right, textvariable=self.legend_var, wraplength=250).pack(pady=6)

    # ----------------- Acciones ----------------------------------------------

    def action_cargar(self):
        df = cargar_datos()
        if df is None:
            return
        self.df_original = df.reset_index(drop=True)
        self.df_sorted = None
        self.current_column = None
        messagebox.showinfo('Datos cargados', f'Datos cargados correctamente ({len(self.df_original)} registros).')
        log(f'Datos cargados: {len(self.df_original)} registros.')
        self._refresh_tree(self.df_original)

    def action_mostrar(self):
        if self.df_original is None:
            messagebox.showwarning('Atención', 'Primero carga un archivo con "Cargar datos".')
            return
        # Dialogo para elegir ver original o ordenado
        choice = messagebox.askquestion('Mostrar', '¿Desea ver los datos ordenados? (Si = ordenados, No = originales)')
        if choice == 'yes' and self.df_sorted is not None:
            self._refresh_tree(self.df_sorted)
            log('Usuario solicitó visualizar datos ordenados.')
        else:
            self._refresh_tree(self.df_original)
            log('Usuario solicitó visualizar datos originales.')

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
                log(f'Búsqueda en columna "{col}" por "{val}": {len(res)} resultados')
                win.destroy()
            except Exception as e:
                messagebox.showerror('Error', f'Error durante la búsqueda: {e}')
                log('Error en búsqueda: ' + str(e))

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
            log(f'Datos guardados en {path}')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo guardar el archivo: {e}')
            log('Error guardando archivo: ' + str(e))

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
                alg_key = 'QuickSort'
            elif method_choice == 'MergeSort (Mezcla)':
                alg_key = 'MergeSort'
            elif method_choice == 'Aleatorio':
                alg_key = random.choice(list(ALGORITHMS.keys()))
            else:
                alg_key = 'QuickSort'

            if not col:
                messagebox.showwarning('Atención', 'Selecciona una columna.')
                return

            # intentar convertir columna a numérica para ordenamiento estable si es posible
            series = self.df_original[col]
            try:
                serie_num = pd.to_numeric(series, errors='coerce')
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
                sorted_values = ALGORITHMS[alg_key](data_list, profiler)
            except Exception as e:
                messagebox.showerror('Error', f'No se pudo ordenar con {alg_key}: {e}')
                log('Error en ordenamiento: ' + str(e) + '\n' + traceback.format_exc())
                return
            end_ns = time.perf_counter_ns()
            elapsed_ns = end_ns - start_ns

            # construir df_sorted reordenando filas completas basadas en la columna
            try:
                # crear mapping viejo->nuevo índice mediante argsort sobre sorted_values
                # para manejar filas completas, usar pandas merge approach
                temp_df = self.df_original.copy()
                temp_df['_sort_key_'] = series.astype(str) if isinstance(sorted_values[0], str) else pd.to_numeric(series, errors='coerce')
                # create a DataFrame with sorted keys
                sorted_df = pd.DataFrame({'_sort_key_': sorted_values})
                # preserve duplicates by adding helper index
                temp_df['_pos_'] = range(len(temp_df))
                sorted_df['_pos_'] = sorted_df.index
                # Perform a stable join: we'll map positions by sorting temp_df by _sort_key_ then taking top N
                try:
                    # first sort original using the selected algorithm on the key values to get indices
                    # Fallback: use pandas sort_values when conversion to numeric succeeded
                    if pd.api.types.is_numeric_dtype(temp_df['_sort_key_']):
                        idx_sorted = temp_df['_sort_key_'].argsort(kind='mergesort')
                    else:
                        idx_sorted = temp_df['_sort_key_'].astype(str).argsort(kind='mergesort')
                    df_result = temp_df.iloc[idx_sorted].drop(columns=['_sort_key_', '_pos_']).reset_index(drop=True)
                except Exception:
                    # fallback: construct result by matching elements sequentially (handles duplicates imperfectly)
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
                log('Error reconstruyendo df_sorted: ' + str(e) + '\n' + traceback.format_exc())
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
            log(f'Ordenado por {alg_key} en {elapsed_ns} ns')
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
            log(f'Treeview actualizado con {min(len(df), MAX_RECORDS)} registros')
        except Exception as e:
            messagebox.showerror('Error', f'No se pudo mostrar la tabla: {e}')
            log('Error en _refresh_tree: ' + str(e) + '\n' + traceback.format_exc())


# --------------------------- Main -----------------------------------------

def main():
    try:
        root = tk.Tk()
        app = SortingApp(root)
        root.geometry('1000x600')
        root.mainloop()
    except Exception as e:
        log('Error fatal en la aplicación: ' + str(e) + '\n' + traceback.format_exc())
        messagebox.showerror('Error fatal', f'La aplicación terminó por un error: {e}')


if __name__ == '__main__':
    main()
