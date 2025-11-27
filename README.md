Proyecto: Métodos de Ordenación y Búsqueda

Equipo 14 – Energía
Integrantes: Héctor Jesús Valadez Pardo, Alberto Román Campos
Materia: Métodos de Ordenación y Búsqueda

⸻

Descripción del Proyecto

Este proyecto implementa una aplicación gráfica en Python que permite analizar y comparar diferentes métodos de ordenación aplicados a conjuntos de datos reales.
A través de una interfaz interactiva desarrollada con tkinter, el usuario puede:
	•	Cargar datos desde archivos .xlsx, .csv o .txt (hasta 10000 registros).
	•	Visualizar los registros antes y después del ordenamiento.
	•	Aplicar distintos métodos de ordenación (QuickSort, MergeSort, Burbuja, etc.).
	•	Medir el rendimiento y tiempo de ejecución (en nanosegundos).
	•	Buscar valores específicos dentro del conjunto de datos.
	•	Exportar los resultados ordenados a un archivo Excel.

⸻

Interfaz Principal

El menú principal contiene las siguientes opciones:

Opción	Descripción
Cargar Datos	Permite seleccionar y cargar un archivo de datos (.xlsx, .csv o .txt).
Mostrar	Visualiza los datos originales o los ordenados dentro de la interfaz.
Ordenar	Abre un submenú donde se elige la columna y el método de ordenamiento.
Buscar	Permite buscar un valor dentro de cualquier columna.
Guardar Excel	Exporta el dataset actual (original u ordenado) a un archivo Excel.
Salir	Cierra la aplicación.


⸻

Métodos de Ordenamiento Implementados

El programa incluye 11 algoritmos de ordenación, cada uno instrumentado para medir operaciones y tiempo:

Tipo	Método	Descripción
Básico	Burbuja (Bubble Sort)	Compara elementos adyacentes e intercambia si es necesario.
Básico	Selección (Selection Sort)	Busca el menor elemento y lo coloca en su posición final.
Básico	Inserción (Insertion Sort)	Inserta cada elemento en la posición correcta dentro de una lista ordenada.
Optimizado	ShellSort	Versión mejorada del método de inserción.
Eficiente	MergeSort	Divide y conquista: divide la lista en sublistas y las combina ordenadas.
Eficiente	QuickSort	Selecciona un pivote y ordena los elementos alrededor de él.
Eficiente	HeapSort	Utiliza una estructura de montículo (heap).
Contado	CountingSort	Cuenta ocurrencias de elementos (enteros).
Numérico	RadixSort	Ordena números dígito a dígito.
Numérico	BucketSort	Distribuye los elementos en cubetas según su valor.
Binario	Inserción Binaria	Inserta utilizando búsqueda binaria.


⸻

Estructura del Proyecto

Metodos_Ordenacion_Proyecto/
│
├── sorting_gui.py                 # Código principal con la interfaz y los algoritmos
├── mod_log.txt                    # Registro automático de acciones y errores
├── sorted_results_by_method.xlsx  # Archivo de salida (si se guarda)
├── README.md                      # Este archivo (documentación)
└── data/                          # (Opcional) Carpeta con archivos de prueba .csv/.xlsx


⸻

Instrucciones de Uso

1.- Requisitos previos

Instala las dependencias necesarias:

pip install pandas openpyxl matplotlib

2.- Ejecutar el programa

python sorting_gui.py

3.- Interactuar con la interfaz
	1.	Presiona “Cargar datos” y selecciona tu archivo.
	2.	Usa “Ordenar” para elegir una columna y método.
	3.	Observa el mensaje final:
“Ordenado por el método QuickSort y se realizó en 253000 nanosegundos.”
	4.	Visualiza los resultados en “Mostrar”.
	5.	Guarda el dataset con “Guardar Excel” si deseas exportarlo.

⸻

Características Técnicas
	•	Lenguaje: Python 3.10+
	•	Interfaz: Tkinter (integrada en Python)
	•	Visualización de datos: matplotlib, ttk.Treeview
	•	Medición de rendimiento: time.perf_counter_ns()
	•	Estructura de almacenamiento: DataFrame de pandas
	•	Límite de carga: 3500 registros

⸻

Ejemplo de uso

(Ejemplo ilustrativo del diseño de la ventana principal)

Leyenda mostrada tras el ordenamiento:

Ordenado por el método QuickSort y se realizó en 123456 nanosegundos.


⸻

Estructura Interna del Programa

Sección	Descripción
Profiler	Clase que cuenta operaciones y registra tiempos.
ALGORITHMS	Diccionario con todos los métodos implementados.
cargar_datos()	Carga y valida archivos, limitando a 3500 registros.
SortingApp	Clase principal de la GUI (ventanas, botones, eventos).
action_ordenar()	Permite seleccionar el método y ejecuta la ordenación.
action_mostrar()	Muestra datos antes o después de ordenar.
action_buscar()	Permite búsquedas en columnas específicas.


⸻

Registro de ejecución

Durante el uso, todas las acciones (carga, ordenamiento, guardado, errores) se registran automáticamente en el archivo:

mod_log.txt

Ejemplo de registro:

[2025-10-28 18:33:42] Archivo datos.xlsx cargado con 3500 registros.
[2025-10-28 18:34:05] Ordenado por QuickSort en 154000 ns.


⸻

Créditos

Equipo 14 – Energía
	•	Héctor Jesús Valadez Pardo
	•	Alberto Román Campos

Materia: Métodos de Ordenación y Búsqueda
Institución: Universidad Autónoma del Estado de Morelos (UAEM)
4 Semestre de la licenciatura en informática.
Año: 2025

⸻

Licencia

Este proyecto es de uso académico y educativo.
