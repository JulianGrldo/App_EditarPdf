#!/usr/bin/env python3
"""Archivo principal de la aplicación Editor de PDF.

Este archivo inicia la aplicación con interfaz gráfica moderna
para editar archivos PDF con una paleta de colores azules.

Autor: Desarrollado paso a paso
Versión: 1.0.0
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

# Añadir el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.gui.main_window import MainWindow
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que todas las dependencias estén instaladas.")
    print("Ejecuta: pip install -r requirements.txt")
    sys.exit(1)


def check_dependencies():
    """Verifica que todas las dependencias estén instaladas."""
    required_modules = [
        'PyPDF2',
        'PIL',
        'fitz',  # PyMuPDF
        'tkinter'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'tkinter':
                import tkinter
            elif module == 'PIL':
                from PIL import Image, ImageTk
            elif module == 'fitz':
                import fitz
            elif module == 'PyPDF2':
                import PyPDF2
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        error_msg = f"Faltan las siguientes dependencias: {', '.join(missing_modules)}\n\n"
        error_msg += "Para instalarlas, ejecuta:\n"
        error_msg += "pip install -r requirements.txt"
        
        print(error_msg)
        
        # Mostrar diálogo de error si tkinter está disponible
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Dependencias Faltantes", error_msg)
            root.destroy()
        except:
            pass
        
        return False
    
    return True


def main():
    """Función principal de la aplicación."""
    print("=" * 50)
    print("    EDITOR DE PDF - APLICACIÓN MODERNA")
    print("=" * 50)
    print("Iniciando aplicación...")
    
    # Verificar dependencias
    if not check_dependencies():
        print("❌ Error: Dependencias faltantes")
        return 1
    
    print("✅ Todas las dependencias están instaladas")
    
    try:
        # Crear y ejecutar la aplicación
        print("🚀 Iniciando interfaz gráfica...")
        app = MainWindow()
        
        print("✅ Aplicación iniciada correctamente")
        print("📄 ¡Listo para editar PDFs!")
        print("-" * 50)
        
        # Ejecutar la aplicación
        app.run()
        
        print("👋 Aplicación cerrada")
        return 0
        
    except Exception as e:
        error_msg = f"Error inesperado al iniciar la aplicación: {e}"
        print(f"❌ {error_msg}")
        
        # Mostrar diálogo de error
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Error de Aplicación", error_msg)
            root.destroy()
        except:
            pass
        
        return 1


if __name__ == "__main__":
    """Punto de entrada de la aplicación."""
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n👋 Aplicación interrumpida por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        sys.exit(1)