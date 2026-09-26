# Tablero de seguimiento de actividades de la construccion del ERP de Exito

---

## Estructura de carpetas
```text
Tablero_Seguimiento_ERP/
│
├── data/                      # Contiene los datos para cargar la gráfica
│
├── src/                       # Código fuente reutilizable (Lógica del proyecto)
│   ├── __init__.py
│   ├── data_loader.py         # Carga de datos y conexiones
│   ├── processing.py          # Aquí se cargan todas las funciones para procesar
│   └── metrics.py             # Cálculo de métricas KPIs
│
├── pages/                     # Páginas del tablero por separado
│   ├── 1_Avance.py            # Muestra de avance de actividades y PMI
│   ├── 2_Resumen_inicial.py   # Vista inicial del dashboard
│   ├── 3_Seguimiento.py       # Seguimiento de objetivos
│   ├── 4_Main.py              # Vista principal
│   └── 5_Riesgos.py           # Levantamiento de riesgos por módulo
│
├── app.py                     # Punto de entrada principal (Landing)
├── requirements.txt           # Dependencias del proyecto
├── .gitignore                 # Archivos excluidos de Git
└── README.md                  # Documentación general del proyecto
```

