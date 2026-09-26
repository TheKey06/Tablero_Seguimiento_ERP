# Tablero de seguimiento de actividades de la construccion del ERP de Exito

---

## Estructura de carpetas

Tablero_Seguimiento_ERP/
│
│
├── data/ # Contiene los datos para cargar la grafica
│
├── src/ # Código fuente reutilizable (Lógica del proyecto)
│ ├── **init**.py
│ ├── data_loader.py # Carga de datos y conexiones
│ ├── processing.py # Aqui se cargan todas las funciones para procesar
│ ├── metrics.py # Calculo de metricas KPIs
│
├── pages/ # Paginas del tablero por separado
│ ├── 1. Avance.py # Muestra de avance de actividades y PMI (Project Manager Intitute)
│ ├── 2. Resumen_inicial.py # Vista inicial del dashboard
│ ├── 3. Seguimiento.py # Seguimiento de objetivos
│ ├── 4. Main.py # Vista inicial del dashboard
│ └── 5. Riesgos.py # Adelantasmiento de riesgos por modulo (estado)
│
├── app.py # Punto de entrada principal (Landing/Página de Inicio)
├── requirements.txt # Dependencias del proyecto (pandas, streamlit, plotly, etc.)
├── .gitignore # Archivos excluidos de control de versiones
└── README.md # Documentación general del proyecto

