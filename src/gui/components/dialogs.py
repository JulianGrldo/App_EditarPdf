"""Diálogos personalizados para la aplicación Editor de PDF.

Este módulo contiene diálogos personalizados con el estilo
y paleta de colores de la aplicación.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple, List

from ...utils.colors import ColorPalette


class CustomDialog:
    """Clase base para diálogos personalizados."""
    
    def __init__(self, parent, title: str, size: Tuple[int, int] = (400, 300)):
        """Inicializa el diálogo personalizado.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            size: Tamaño del diálogo (ancho, alto)
        """
        self.parent = parent
        self.result = None
        
        # Crear ventana
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry(f"{size[0]}x{size[1]}")
        self.dialog.configure(bg=ColorPalette.BACKGROUND)
        self.dialog.resizable(False, False)
        
        # Centrar diálogo
        self._center_dialog(size)
        
        # Hacer modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Configurar estilos
        self._setup_styles()
        
        # Frame principal
        self.main_frame = ttk.Frame(self.dialog, style='Card.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    def _center_dialog(self, size: Tuple[int, int]):
        """Centra el diálogo en la pantalla."""
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (size[0] // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (size[1] // 2)
        self.dialog.geometry(f"{size[0]}x{size[1]}+{x}+{y}")
    
    def _setup_styles(self):
        """Configura estilos para el diálogo."""
        self.style = ttk.Style()
        
        # Estilo para frames de diálogo
        self.style.configure(
            'Dialog.TFrame',
            background=ColorPalette.CARD_BACKGROUND,
            relief='flat'
        )
        
        # Estilo para labels de diálogo
        self.style.configure(
            'DialogTitle.TLabel',
            background=ColorPalette.CARD_BACKGROUND,
            foreground=ColorPalette.TEXT_PRIMARY,
            font=('Segoe UI', 14, 'bold')
        )
        
        self.style.configure(
            'DialogText.TLabel',
            background=ColorPalette.CARD_BACKGROUND,
            foreground=ColorPalette.TEXT_SECONDARY,
            font=('Segoe UI', 10)
        )
    
    def show(self):
        """Muestra el diálogo y retorna el resultado."""
        self.dialog.wait_window()
        return self.result


class TextInputDialog(CustomDialog):
    """Diálogo para entrada de texto."""
    
    def __init__(self, parent, title: str, prompt: str, default_text: str = ""):
        """Inicializa el diálogo de entrada de texto.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            prompt: Texto del prompt
            default_text: Texto por defecto
        """
        super().__init__(parent, title, (450, 200))
        self.prompt = prompt
        self.default_text = default_text
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Título
        title_label = ttk.Label(
            self.main_frame,
            text=self.prompt,
            style='DialogTitle.TLabel'
        )
        title_label.pack(pady=(0, 20))
        
        # Campo de entrada
        self.entry = tk.Entry(
            self.main_frame,
            font=('Segoe UI', 11),
            bg=ColorPalette.LIGHT_BLUE,
            fg=ColorPalette.TEXT_PRIMARY,
            relief='flat',
            bd=5
        )
        self.entry.pack(fill='x', pady=(0, 20))
        self.entry.insert(0, self.default_text)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # Botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x')
        
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancelar",
            style='Secondary.TButton',
            command=self._cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        ok_btn = ttk.Button(
            button_frame,
            text="Aceptar",
            style='Primary.TButton',
            command=self._ok
        )
        ok_btn.pack(side='right')
        
        # Bind Enter key
        self.entry.bind('<Return>', lambda e: self._ok())
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _ok(self):
        """Maneja el botón Aceptar."""
        self.result = self.entry.get().strip()
        self.dialog.destroy()
    
    def _cancel(self):
        """Maneja el botón Cancelar."""
        self.result = None
        self.dialog.destroy()


class PageSelectionDialog(CustomDialog):
    """Diálogo para selección de páginas."""
    
    def __init__(self, parent, title: str, total_pages: int):
        """Inicializa el diálogo de selección de páginas.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
            total_pages: Número total de páginas
        """
        super().__init__(parent, title, (500, 400))
        self.total_pages = total_pages
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Título
        title_label = ttk.Label(
            self.main_frame,
            text=f"Seleccionar páginas (Total: {self.total_pages})",
            style='DialogTitle.TLabel'
        )
        title_label.pack(pady=(0, 15))
        
        # Opciones de selección
        self.selection_var = tk.StringVar(value="current")
        
        # Página actual
        current_radio = ttk.Radiobutton(
            self.main_frame,
            text="Página actual",
            variable=self.selection_var,
            value="current"
        )
        current_radio.pack(anchor='w', pady=2)
        
        # Todas las páginas
        all_radio = ttk.Radiobutton(
            self.main_frame,
            text="Todas las páginas",
            variable=self.selection_var,
            value="all"
        )
        all_radio.pack(anchor='w', pady=2)
        
        # Rango personalizado
        range_radio = ttk.Radiobutton(
            self.main_frame,
            text="Rango personalizado:",
            variable=self.selection_var,
            value="range"
        )
        range_radio.pack(anchor='w', pady=2)
        
        # Frame para rango
        range_frame = ttk.Frame(self.main_frame)
        range_frame.pack(fill='x', padx=(20, 0), pady=(5, 15))
        
        ttk.Label(range_frame, text="Desde:").pack(side='left')
        
        self.start_entry = tk.Entry(
            range_frame,
            width=5,
            font=('Segoe UI', 10),
            bg=ColorPalette.LIGHT_BLUE
        )
        self.start_entry.pack(side='left', padx=(5, 10))
        
        ttk.Label(range_frame, text="Hasta:").pack(side='left')
        
        self.end_entry = tk.Entry(
            range_frame,
            width=5,
            font=('Segoe UI', 10),
            bg=ColorPalette.LIGHT_BLUE
        )
        self.end_entry.pack(side='left', padx=(5, 0))
        
        # Lista de páginas seleccionadas
        list_radio = ttk.Radiobutton(
            self.main_frame,
            text="Páginas específicas:",
            variable=self.selection_var,
            value="list"
        )
        list_radio.pack(anchor='w', pady=2)
        
        # Frame para lista
        list_frame = ttk.Frame(self.main_frame)
        list_frame.pack(fill='x', padx=(20, 0), pady=(5, 15))
        
        ttk.Label(
            list_frame,
            text="Páginas (separadas por comas):",
            style='DialogText.TLabel'
        ).pack(anchor='w')
        
        self.pages_entry = tk.Entry(
            list_frame,
            font=('Segoe UI', 10),
            bg=ColorPalette.LIGHT_BLUE
        )
        self.pages_entry.pack(fill='x', pady=(5, 0))
        
        # Botones
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancelar",
            style='Secondary.TButton',
            command=self._cancel
        )
        cancel_btn.pack(side='right', padx=(10, 0))
        
        ok_btn = ttk.Button(
            button_frame,
            text="Aceptar",
            style='Primary.TButton',
            command=self._ok
        )
        ok_btn.pack(side='right')
        
        # Bind Escape key
        self.dialog.bind('<Escape>', lambda e: self._cancel())
    
    def _ok(self):
        """Maneja el botón Aceptar."""
        selection_type = self.selection_var.get()
        
        try:
            if selection_type == "current":
                self.result = [0]  # Se ajustará en la ventana principal
            elif selection_type == "all":
                self.result = list(range(self.total_pages))
            elif selection_type == "range":
                start = int(self.start_entry.get()) - 1
                end = int(self.end_entry.get()) - 1
                if start < 0 or end >= self.total_pages or start > end:
                    raise ValueError("Rango inválido")
                self.result = list(range(start, end + 1))
            elif selection_type == "list":
                pages_text = self.pages_entry.get().strip()
                if not pages_text:
                    raise ValueError("No se especificaron páginas")
                pages = [int(p.strip()) - 1 for p in pages_text.split(',')]
                for page in pages:
                    if page < 0 or page >= self.total_pages:
                        raise ValueError(f"Página {page + 1} fuera de rango")
                self.result = sorted(set(pages))
            
            self.dialog.destroy()
            
        except ValueError as e:
            messagebox.showerror(
                "Error",
                f"Selección inválida: {e}",
                parent=self.dialog
            )
    
    def _cancel(self):
        """Maneja el botón Cancelar."""
        self.result = None
        self.dialog.destroy()


class AboutDialog(CustomDialog):
    """Diálogo Acerca de la aplicación."""
    
    def __init__(self, parent):
        """Inicializa el diálogo Acerca de."""
        super().__init__(parent, "Acerca de Editor de PDF", (450, 350))
        self._create_widgets()
    
    def _create_widgets(self):
        """Crea los widgets del diálogo."""
        # Icono y título
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Título principal
        title_label = ttk.Label(
            header_frame,
            text="📄 Editor de PDF",
            style='DialogTitle.TLabel',
            font=('Segoe UI', 18, 'bold')
        )
        title_label.pack()
        
        # Versión
        version_label = ttk.Label(
            header_frame,
            text="Versión 1.0.0",
            style='DialogText.TLabel'
        )
        version_label.pack(pady=(5, 0))
        
        # Descripción
        desc_text = (
            "Una aplicación moderna para editar archivos PDF\n"
            "con una interfaz intuitiva y diseño en tonos azules.\n\n"
            "Características principales:\n"
            "• Visualización de PDFs\n"
            "• Rotación de páginas\n"
            "• Extracción de páginas\n"
            "• Fusión de PDFs\n"
            "• Adición de texto\n"
            "• Interfaz moderna y amigable"
        )
        
        desc_label = ttk.Label(
            self.main_frame,
            text=desc_text,
            style='DialogText.TLabel',
            justify='left'
        )
        desc_label.pack(pady=(0, 20))
        
        # Información del desarrollador
        dev_frame = ttk.Frame(self.main_frame)
        dev_frame.pack(fill='x', pady=(0, 20))
        
        dev_label = ttk.Label(
            dev_frame,
            text="Desarrollado paso a paso con Python y tkinter",
            style='DialogText.TLabel',
            font=('Segoe UI', 9, 'italic')
        )
        dev_label.pack()
        
        # Botón cerrar
        close_btn = ttk.Button(
            self.main_frame,
            text="Cerrar",
            style='Primary.TButton',
            command=self._close
        )
        close_btn.pack()
        
        # Bind Escape key
        self.dialog.bind('<Escape>', lambda e: self._close())
    
    def _close(self):
        """Cierra el diálogo."""
        self.dialog.destroy()


def show_text_input(parent, title: str, prompt: str, default_text: str = "") -> Optional[str]:
    """Muestra un diálogo de entrada de texto.
    
    Args:
        parent: Ventana padre
        title: Título del diálogo
        prompt: Texto del prompt
        default_text: Texto por defecto
        
    Returns:
        Texto ingresado o None si se canceló
    """
    dialog = TextInputDialog(parent, title, prompt, default_text)
    return dialog.show()


def show_page_selection(parent, title: str, total_pages: int) -> Optional[List[int]]:
    """Muestra un diálogo de selección de páginas.
    
    Args:
        parent: Ventana padre
        title: Título del diálogo
        total_pages: Número total de páginas
        
    Returns:
        Lista de páginas seleccionadas o None si se canceló
    """
    dialog = PageSelectionDialog(parent, title, total_pages)
    return dialog.show()


def show_about(parent):
    """Muestra el diálogo Acerca de.
    
    Args:
        parent: Ventana padre
    """
    dialog = AboutDialog(parent)
    dialog.show()