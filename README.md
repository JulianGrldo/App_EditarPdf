# Editor de PDF - Aplicación Python

Una aplicación moderna para editar archivos PDF con una interfaz intuitiva y diseño en tonos azules.

## Características

- Interfaz gráfica moderna con tkinter
- Edición de texto en PDFs
- Rotación de páginas
- Fusión de PDFs
- Extracción de páginas
- Diseño con paleta de colores azules para tranquilidad

## Instalación

1. Crear ambiente virtual:
```bash
python -m venv venv
```

2. Activar ambiente virtual:
```bash
# Windows
venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

## Estructura del Proyecto

```
App_EditarPdf/
├── main.py              # Archivo principal
├── src/
│   ├── __init__.py
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   └── components/
│   ├── pdf_editor/
│   │   ├── __init__.py
│   │   └── editor.py
│   └── utils/
│       ├── __init__.py
│       └── colors.py
├── requirements.txt
└── README.md
```

