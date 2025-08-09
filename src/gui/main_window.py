"""Ventana principal de la aplicación Editor de PDF.

Esta ventana contiene la interfaz principal con todos los controles
y funcionalidades para editar archivos PDF.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import io
import os
from typing import Optional

from ..utils.colors import ColorPalette
from ..pdf_editor.editor import PDFEditor
from .components.dialogs import show_text_input, show_page_selection, show_about


class MainWindow:
    """Ventana principal de la aplicación."""
    
    def __init__(self):
        """Inicializa la ventana principal."""
        self.root = tk.Tk()
        self.pdf_editor = PDFEditor()
        self.current_page = 0
        self.zoom_level = 1.0
        self.pdf_image = None
        self.edit_mode = False
        self.dragging = False
        self.drag_start = None
        self.canvas_elements = {}  # {element_id: canvas_item_id}
        
        self._setup_window()
        self._create_styles()
        self._create_widgets()
        self._setup_layout()
        self._bind_events()
    
    def _setup_window(self):
        """Configura la ventana principal."""
        self.root.title("Editor de PDF - Aplicación Moderna")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.root.configure(bg=ColorPalette.BACKGROUND)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1200 // 2)
        y = (self.root.winfo_screenheight() // 2) - (800 // 2)
        self.root.geometry(f"1200x800+{x}+{y}")
    
    def _create_styles(self):
        """Crea estilos personalizados para los widgets."""
        self.style = ttk.Style()
        
        # Configurar tema
        self.style.theme_use('clam')
        
        # Estilo para botones principales
        self.style.configure(
            'Primary.TButton',
            background=ColorPalette.BUTTON_PRIMARY,
            foreground=ColorPalette.TEXT_WHITE,
            borderwidth=0,
            focuscolor='none',
            padding=(20, 10)
        )
        
        self.style.map(
            'Primary.TButton',
            background=[('active', ColorPalette.BUTTON_PRIMARY_HOVER)]
        )
        
        # Estilo para botones secundarios
        self.style.configure(
            'Secondary.TButton',
            background=ColorPalette.BUTTON_SECONDARY,
            foreground=ColorPalette.TEXT_PRIMARY,
            borderwidth=1,
            focuscolor='none',
            padding=(15, 8)
        )
        
        # Estilo para frames
        self.style.configure(
            'Card.TFrame',
            background=ColorPalette.CARD_BACKGROUND,
            relief='flat',
            borderwidth=1
        )
        
        # Estilo para labels
        self.style.configure(
            'Title.TLabel',
            background=ColorPalette.CARD_BACKGROUND,
            foreground=ColorPalette.TEXT_PRIMARY,
            font=('Segoe UI', 16, 'bold')
        )
        
        self.style.configure(
            'Subtitle.TLabel',
            background=ColorPalette.CARD_BACKGROUND,
            foreground=ColorPalette.TEXT_SECONDARY,
            font=('Segoe UI', 10)
        )
    
    def _create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal
        self.main_frame = ttk.Frame(self.root)
        
        # Barra de herramientas superior
        self._create_toolbar()
        
        # Panel lateral izquierdo
        self._create_sidebar()
        
        # Área central de visualización
        self._create_viewer_area()
        
        # Panel de propiedades derecho
        self._create_properties_panel()
        
        # Barra de estado
        self._create_status_bar()
    
    def _create_toolbar(self):
        """Crea la barra de herramientas superior."""
        self.toolbar_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Botones principales
        self.btn_open = ttk.Button(
            self.toolbar_frame,
            text="📁 Abrir PDF",
            style='Primary.TButton',
            command=self.open_pdf
        )
        
        self.btn_save = ttk.Button(
            self.toolbar_frame,
            text="💾 Guardar",
            style='Secondary.TButton',
            command=self.save_pdf,
            state='disabled'
        )
        
        self.btn_save_as = ttk.Button(
            self.toolbar_frame,
            text="📄 Guardar Como",
            style='Secondary.TButton',
            command=self.save_pdf_as,
            state='disabled'
        )
        
        # Separador
        separator1 = ttk.Separator(self.toolbar_frame, orient='vertical')
        
        # Controles de zoom
        self.btn_zoom_out = ttk.Button(
            self.toolbar_frame,
            text="🔍-",
            style='Secondary.TButton',
            command=self.zoom_out,
            state='disabled'
        )
        
        self.zoom_label = ttk.Label(
            self.toolbar_frame,
            text="100%",
            style='Subtitle.TLabel'
        )
        
        self.btn_zoom_in = ttk.Button(
            self.toolbar_frame,
            text="🔍+",
            style='Secondary.TButton',
            command=self.zoom_in,
            state='disabled'
        )
        
        # Empaquetar botones
        self.btn_open.pack(side='left', padx=(10, 5), pady=10)
        self.btn_save.pack(side='left', padx=5, pady=10)
        self.btn_save_as.pack(side='left', padx=5, pady=10)
        separator1.pack(side='left', fill='y', padx=10, pady=5)
        self.btn_zoom_out.pack(side='left', padx=5, pady=10)
        self.zoom_label.pack(side='left', padx=5, pady=10)
        self.btn_zoom_in.pack(side='left', padx=5, pady=10)
    
    def _create_sidebar(self):
        """Crea el panel lateral izquierdo."""
        self.sidebar_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Título del panel
        title_label = ttk.Label(
            self.sidebar_frame,
            text="Herramientas",
            style='Title.TLabel'
        )
        title_label.pack(pady=(15, 10), padx=15, anchor='w')
        
        # Sección de páginas
        pages_frame = ttk.LabelFrame(
            self.sidebar_frame,
            text="Páginas",
            padding=10
        )
        pages_frame.pack(fill='x', padx=15, pady=5)
        
        self.btn_rotate_left = ttk.Button(
            pages_frame,
            text="↺ Rotar Izq",
            style='Secondary.TButton',
            command=self.rotate_left,
            state='disabled'
        )
        
        self.btn_rotate_right = ttk.Button(
            pages_frame,
            text="↻ Rotar Der",
            style='Secondary.TButton',
            command=self.rotate_right,
            state='disabled'
        )
        
        self.btn_extract = ttk.Button(
            pages_frame,
            text="📄 Extraer",
            style='Secondary.TButton',
            command=self.extract_pages,
            state='disabled'
        )
        
        self.btn_rotate_left.pack(fill='x', pady=2)
        self.btn_rotate_right.pack(fill='x', pady=2)
        self.btn_extract.pack(fill='x', pady=2)
        
        # Sección de texto
        text_frame = ttk.LabelFrame(
            self.sidebar_frame,
            text="Edición",
            padding=10
        )
        text_frame.pack(fill='x', padx=15, pady=5)
        
        self.btn_edit_mode = ttk.Button(
            text_frame,
            text="✏️ Modo Edición",
            style='Secondary.TButton',
            command=self.toggle_edit_mode,
            state='disabled'
        )
        
        self.btn_add_text = ttk.Button(
            text_frame,
            text="📝 Añadir Texto",
            style='Secondary.TButton',
            command=self.add_text,
            state='disabled'
        )
        
        self.btn_add_image = ttk.Button(
            text_frame,
            text="🖼️ Añadir Imagen",
            style='Secondary.TButton',
            command=self.add_image,
            state='disabled'
        )
        
        self.btn_edit_mode.pack(fill='x', pady=2)
        self.btn_add_text.pack(fill='x', pady=2)
        self.btn_add_image.pack(fill='x', pady=2)
        
        # Sección de fusión
        merge_frame = ttk.LabelFrame(
            self.sidebar_frame,
            text="Fusión",
            padding=10
        )
        merge_frame.pack(fill='x', padx=15, pady=5)
        
        self.btn_merge = ttk.Button(
            merge_frame,
            text="🔗 Fusionar PDFs",
            style='Secondary.TButton',
            command=self.merge_pdfs
        )
        
        self.btn_merge.pack(fill='x', pady=2)
        
        # Sección de ayuda
        help_frame = ttk.LabelFrame(
            self.sidebar_frame,
            text="Ayuda",
            padding=10
        )
        help_frame.pack(fill='x', padx=15, pady=5)
        
        self.btn_about = ttk.Button(
            help_frame,
            text="ℹ️ Acerca de",
            style='Secondary.TButton',
            command=self.show_about
        )
        
        self.btn_about.pack(fill='x', pady=2)
    
    def _create_viewer_area(self):
        """Crea el área central de visualización."""
        self.viewer_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Canvas para mostrar el PDF
        self.canvas_frame = ttk.Frame(self.viewer_frame)
        self.canvas_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.canvas = tk.Canvas(
            self.canvas_frame,
            bg=ColorPalette.LIGHT_BLUE,
            highlightthickness=0
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Bind eventos del canvas
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)
        self.canvas.bind("<Double-Button-1>", self.on_canvas_double_click)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Key>", self.on_canvas_key)
        self.canvas.focus_set()
        
        # Empaquetar canvas y scrollbars
        self.canvas.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        self.canvas_frame.grid_rowconfigure(0, weight=1)
        self.canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Controles de navegación
        nav_frame = ttk.Frame(self.viewer_frame)
        nav_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.btn_prev = ttk.Button(
            nav_frame,
            text="◀ Anterior",
            style='Secondary.TButton',
            command=self.prev_page,
            state='disabled'
        )
        
        self.page_label = ttk.Label(
            nav_frame,
            text="Página: - / -",
            style='Subtitle.TLabel'
        )
        
        self.btn_next = ttk.Button(
            nav_frame,
            text="Siguiente ▶",
            style='Secondary.TButton',
            command=self.next_page,
            state='disabled'
        )
        
        self.btn_prev.pack(side='left', padx=5)
        self.page_label.pack(side='left', expand=True)
        self.btn_next.pack(side='right', padx=5)
        
        # Mensaje de bienvenida
        self._show_welcome_message()
    
    def _create_properties_panel(self):
        """Crea el panel de propiedades derecho."""
        self.properties_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        # Título
        title_label = ttk.Label(
            self.properties_frame,
            text="Propiedades",
            style='Title.TLabel'
        )
        title_label.pack(pady=(15, 10), padx=15, anchor='w')
        
        # Área de texto para mostrar información
        self.info_text = scrolledtext.ScrolledText(
            self.properties_frame,
            width=25,
            height=20,
            bg=ColorPalette.LIGHT_BLUE,
            fg=ColorPalette.TEXT_PRIMARY,
            font=('Consolas', 9),
            state='disabled'
        )
        self.info_text.pack(fill='both', expand=True, padx=15, pady=(0, 15))
    
    def _create_status_bar(self):
        """Crea la barra de estado inferior."""
        self.status_frame = ttk.Frame(self.main_frame, style='Card.TFrame')
        
        self.status_label = ttk.Label(
            self.status_frame,
            text="Listo",
            style='Subtitle.TLabel'
        )
        self.status_label.pack(side='left', padx=10, pady=5)
    
    def _setup_layout(self):
        """Configura el layout de la ventana."""
        self.main_frame.pack(fill='both', expand=True)
        
        # Configurar grid
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)
        
        # Posicionar frames
        self.toolbar_frame.grid(row=0, column=0, columnspan=3, sticky='ew', pady=(0, 1))
        self.sidebar_frame.grid(row=1, column=0, sticky='nsew', padx=(0, 1))
        self.viewer_frame.grid(row=1, column=1, sticky='nsew', padx=1)
        self.properties_frame.grid(row=1, column=2, sticky='nsew', padx=(1, 0))
        self.status_frame.grid(row=2, column=0, columnspan=3, sticky='ew', pady=(1, 0))
        
        # Configurar pesos de columnas
        self.main_frame.grid_columnconfigure(0, weight=0, minsize=200)
        self.main_frame.grid_columnconfigure(1, weight=1, minsize=400)
        self.main_frame.grid_columnconfigure(2, weight=0, minsize=250)
    
    def _bind_events(self):
        """Vincula eventos de la interfaz."""
        self.root.bind('<Control-o>', lambda e: self.open_pdf())
        self.root.bind('<Control-s>', lambda e: self.save_pdf())
        self.root.bind('<Control-Shift-S>', lambda e: self.save_pdf_as())
        self.canvas.bind('<Button-1>', self.on_canvas_click)
    
    def _show_welcome_message(self):
        """Muestra mensaje de bienvenida en el canvas."""
        self.canvas.delete('all')
        
        # Crear texto de bienvenida
        welcome_text = "📄 Editor de PDF\n\n" \
                      "Haz clic en 'Abrir PDF' para comenzar\n" \
                      "o arrastra un archivo aquí"
        
        self.canvas.create_text(
            400, 300,
            text=welcome_text,
            font=('Segoe UI', 16),
            fill=ColorPalette.TEXT_SECONDARY,
            justify='center'
        )
    
    def update_status(self, message: str):
        """Actualiza el mensaje de la barra de estado."""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def run(self):
        """Inicia la aplicación."""
        self.root.mainloop()
    
    # Métodos de funcionalidad (continuarán en la siguiente parte)
    def open_pdf(self):
        """Abre un archivo PDF."""
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo PDF",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if file_path:
            self.update_status("Cargando PDF...")
            if self.pdf_editor.load_pdf(file_path):
                self.current_page = 0
                self._enable_controls()
                self._update_display()
                self._update_info_panel()
                self.update_status(f"PDF cargado: {file_path}")
            else:
                messagebox.showerror("Error", "No se pudo cargar el archivo PDF")
                self.update_status("Error al cargar PDF")
    
    def save_pdf(self):
        """Guarda el PDF actual."""
        if self.pdf_editor.current_pdf:
            if self.pdf_editor.save_pdf():
                self.update_status("PDF guardado")
                messagebox.showinfo("Éxito", "PDF guardado correctamente")
            else:
                messagebox.showerror("Error", "No se pudo guardar el PDF")
    
    def save_pdf_as(self):
        """Guarda el PDF con un nuevo nombre."""
        if self.pdf_editor.current_pdf:
            file_path = filedialog.asksaveasfilename(
                title="Guardar PDF como",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")]
            )
            
            if file_path:
                if self.pdf_editor.save_pdf(file_path):
                    self.update_status(f"PDF guardado como: {file_path}")
                    messagebox.showinfo("Éxito", "PDF guardado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo guardar el PDF")
    
    def _enable_controls(self):
        """Habilita los controles cuando se carga un PDF."""
        controls = [
            self.btn_save, self.btn_save_as, self.btn_zoom_in, self.btn_zoom_out,
            self.btn_rotate_left, self.btn_rotate_right, self.btn_extract,
            self.btn_add_text, self.btn_add_image, self.btn_edit_mode, 
            self.btn_prev, self.btn_next
        ]
        
        for control in controls:
            control.config(state='normal')
    
    def _update_display(self):
        """Actualiza la visualización del PDF."""
        if not self.pdf_editor.current_pdf:
            return
        
        try:
            # Obtener imagen de la página actual
            image_data = self.pdf_editor.get_page_image(self.current_page, self.zoom_level)
            
            if image_data:
                # Convertir a imagen de PIL
                image = Image.open(io.BytesIO(image_data))
                self.photo = ImageTk.PhotoImage(image)
                
                # Limpiar canvas y mostrar imagen
                self.canvas.delete('all')
                self.canvas_elements.clear()
                
                self.canvas.create_image(10, 10, anchor='nw', image=self.photo)
                
                # Mostrar elementos editables si está en modo edición
                if self.edit_mode:
                    self._draw_editable_elements()
                
                # Actualizar scroll region
                self.canvas.configure(scrollregion=self.canvas.bbox('all'))
                
                # Actualizar etiqueta de página
                total_pages = self.pdf_editor.get_page_count()
                self.page_label.config(text=f"Página: {self.current_page + 1} / {total_pages}")
                
                # Actualizar zoom
                self.zoom_label.config(text=f"{int(self.zoom_level * 100)}%")
        except Exception as e:
            print(f"Error al actualizar display: {e}")
    
    def _draw_editable_elements(self):
        """Dibuja los elementos editables en el canvas."""
        try:
            elements = self.pdf_editor.get_page_elements(self.current_page)
            
            for element in elements:
                x, y = element.position
                w, h = element.size
                
                if element.type == 'text':
                    # Dibujar texto
                    text_id = self.canvas.create_text(
                        x + 10, y + 10,  # Offset por la imagen
                        text=element.content,
                        anchor="nw",
                        font=("Arial", element.font_size),
                        fill=element.color,
                        tags="editable"
                    )
                    
                    # Dibujar borde si está seleccionado
                    if element.selected:
                        bbox = self.canvas.bbox(text_id)
                        if bbox:
                            border_id = self.canvas.create_rectangle(
                                bbox[0]-2, bbox[1]-2, bbox[2]+2, bbox[3]+2,
                                outline=ColorPalette.ACCENT,
                                width=2,
                                dash=(5, 5),
                                tags="selection"
                            )
                            self.canvas_elements[element.id] = (text_id, border_id)
                        else:
                            self.canvas_elements[element.id] = (text_id, None)
                    else:
                        self.canvas_elements[element.id] = (text_id, None)
                
                elif element.type == 'image':
                    try:
                        # Cargar y redimensionar imagen
                        img = Image.open(element.content)
                        img = img.resize((int(w), int(h)), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(img)
                        
                        # Dibujar imagen
                        image_id = self.canvas.create_image(
                            x + 10, y + 10,  # Offset por la imagen
                            anchor="nw",
                            image=photo,
                            tags="editable"
                        )
                        
                        # Mantener referencia a la imagen
                        if not hasattr(self.canvas, 'image_refs'):
                            self.canvas.image_refs = []
                        self.canvas.image_refs.append(photo)
                        
                        # Dibujar borde si está seleccionado
                        if element.selected:
                            border_id = self.canvas.create_rectangle(
                                x + 8, y + 8, x + w + 12, y + h + 12,
                                outline=ColorPalette.ACCENT,
                                width=2,
                                dash=(5, 5),
                                tags="selection"
                            )
                            self.canvas_elements[element.id] = (image_id, border_id)
                        else:
                            self.canvas_elements[element.id] = (image_id, None)
                            
                    except Exception as e:
                        print(f"Error al cargar imagen {element.content}: {e}")
                        # Dibujar rectángulo como placeholder
                        rect_id = self.canvas.create_rectangle(
                            x + 10, y + 10, x + w + 10, y + h + 10,
                            outline="red",
                            fill="lightgray",
                            tags="editable"
                        )
                        self.canvas_elements[element.id] = (rect_id, None)
        except Exception as e:
            print(f"Error al dibujar elementos editables: {e}")
    
    def _update_info_panel(self):
        """Actualiza el panel de información."""
        if not self.pdf_editor.current_pdf:
            return
        
        info = self.pdf_editor.get_pdf_info()
        
        info_text = f"""INFORMACIÓN DEL PDF
{'=' * 25}

Título: {info.get('title', 'N/A')}
Autor: {info.get('author', 'N/A')}
Asunto: {info.get('subject', 'N/A')}
Creador: {info.get('creator', 'N/A')}
Productor: {info.get('producer', 'N/A')}

Páginas: {info.get('page_count', 0)}
Tamaño: {info.get('file_size', 0) / 1024:.1f} KB

Fecha creación: {info.get('creation_date', 'N/A')}
Fecha modificación: {info.get('modification_date', 'N/A')}
"""
        
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.insert(1.0, info_text)
        self.info_text.config(state='disabled')
    
    def prev_page(self):
        """Va a la página anterior."""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_display()
    
    def next_page(self):
        """Va a la página siguiente."""
        if self.current_page < self.pdf_editor.get_page_count() - 1:
            self.current_page += 1
            self._update_display()
    
    def zoom_in(self):
        """Aumenta el zoom."""
        if self.zoom_level < 3.0:
            self.zoom_level += 0.25
            self._update_display()
    
    def zoom_out(self):
        """Disminuye el zoom."""
        if self.zoom_level > 0.25:
            self.zoom_level -= 0.25
            self._update_display()
    
    def rotate_left(self):
        """Rota la página actual 90° a la izquierda."""
        if self.pdf_editor.rotate_page(self.current_page, -90):
            self._update_display()
            self.update_status("Página rotada 90° izquierda")
    
    def rotate_right(self):
        """Rota la página actual 90° a la derecha."""
        if self.pdf_editor.rotate_page(self.current_page, 90):
            self._update_display()
            self.update_status("Página rotada 90° derecha")
    
    def extract_pages(self):
        """Extrae páginas seleccionadas."""
        if not self.pdf_editor.current_pdf:
            return
        
        # Mostrar diálogo de selección de páginas
        total_pages = self.pdf_editor.get_page_count()
        selected_pages = show_page_selection(
            self.root,
            "Extraer Páginas",
            total_pages
        )
        
        if selected_pages is not None:
            # Ajustar página actual si se seleccionó "current"
            if len(selected_pages) == 1 and selected_pages[0] == 0:
                selected_pages = [self.current_page]
            
            file_path = filedialog.asksaveasfilename(
                title="Guardar páginas extraídas",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")]
            )
            
            if file_path:
                if self.pdf_editor.extract_pages(selected_pages, file_path):
                    pages_text = ", ".join([str(p + 1) for p in selected_pages])
                    messagebox.showinfo(
                        "Éxito", 
                        f"Páginas {pages_text} extraídas correctamente"
                    )
                    self.update_status(f"Páginas extraídas: {len(selected_pages)}")
                else:
                    messagebox.showerror("Error", "No se pudieron extraer las páginas")
    
    def add_text(self):
        """Añade texto a la página actual."""
        if not self.pdf_editor.current_pdf:
            return
        
        # Mostrar diálogo personalizado para entrada de texto
        text = show_text_input(
            self.root,
            "Añadir Texto",
            "Ingrese el texto que desea añadir:",
            ""
        )
        
        if text:
            # Añadir en el centro de la página
            center_x = 200
            center_y = 200
            
            try:
                element = self.pdf_editor.add_text_element(
                    self.current_page, 
                    text, 
                    (center_x, center_y),
                    font_size=12,
                    color="black"
                )
                
                self._update_display()
                self.update_status(f"Texto añadido: '{text[:20]}...'")
                messagebox.showinfo("Éxito", "Texto añadido correctamente")
                
                # Activar modo edición si no está activo
                if not self.edit_mode:
                    self.toggle_edit_mode()
                    
            except Exception as e:
                print(f"Error al añadir texto: {e}")
                messagebox.showerror("Error", "No se pudo añadir el texto")
    
    def merge_pdfs(self):
        """Fusiona múltiples PDFs."""
        file_paths = filedialog.askopenfilenames(
            title="Seleccionar PDFs para fusionar",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        
        if len(file_paths) > 1:
            output_path = filedialog.asksaveasfilename(
                title="Guardar PDF fusionado",
                defaultextension=".pdf",
                filetypes=[("Archivos PDF", "*.pdf")]
            )
            
            if output_path:
                if self.pdf_editor.merge_pdfs(list(file_paths), output_path):
                    messagebox.showinfo("Éxito", "PDFs fusionados correctamente")
                    self.update_status("PDFs fusionados")
                else:
                    messagebox.showerror("Error", "No se pudieron fusionar los PDFs")
    
    def show_about(self):
        """Muestra el diálogo Acerca de."""
        show_about(self.root)
    
    def toggle_edit_mode(self):
        """Alterna el modo de edición."""
        if not self.pdf_editor.current_pdf:
            return
        
        self.edit_mode = not self.edit_mode
        
        if self.edit_mode:
            self.btn_edit_mode.config(text="🔒 Bloquear")
            self.update_status("Modo edición activado - Haga clic para seleccionar elementos")
            self.canvas.config(cursor="crosshair")
            self.btn_add_text.config(state='normal')
            self.btn_add_image.config(state='normal')
        else:
            self.btn_edit_mode.config(text="✏️ Modo Edición")
            self.update_status("Modo edición desactivado")
            self.canvas.config(cursor="")
        
        self._update_display()
    
    def add_image(self):
        """Añade una imagen al PDF."""
        if not self.pdf_editor.current_pdf:
            return
        
        # Seleccionar archivo de imagen
        image_file = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[
                ("Imágenes", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if image_file:
            try:
                # Añadir imagen en el centro de la página
                center_x = 200
                center_y = 200
                
                element = self.pdf_editor.add_image_element(
                    self.current_page, 
                    image_file, 
                    (center_x, center_y),
                    (150, 150)  # Tamaño por defecto
                )
                
                self._update_display()
                self.update_status(f"Imagen añadida: {os.path.basename(image_file)}")
                messagebox.showinfo("Éxito", "Imagen añadida correctamente")
                
                # Activar modo edición si no está activo
                if not self.edit_mode:
                    self.toggle_edit_mode()
                    
            except Exception as e:
                print(f"Error al añadir imagen: {e}")
                messagebox.showerror("Error", "No se pudo añadir la imagen")
    
    def on_canvas_click(self, event):
        """Maneja clics en el canvas."""
        if not self.edit_mode or not self.pdf_editor.current_pdf:
            return
        
        # Convertir coordenadas del canvas a coordenadas del PDF
        canvas_x = self.canvas.canvasx(event.x) - 10  # Ajustar por offset de imagen
        canvas_y = self.canvas.canvasy(event.y) - 10
        
        # Intentar seleccionar elemento en la posición
        selected = self.pdf_editor.select_element_at_position(self.current_page, (canvas_x, canvas_y))
        
        if selected:
            self.update_status(f"Elemento seleccionado: {selected.type} - {selected.content[:30] if selected.type == 'text' else 'imagen'}")
            self.drag_start = (canvas_x, canvas_y)
        else:
            self.pdf_editor.clear_selection()
            self.update_status(f"Posición: ({int(canvas_x)}, {int(canvas_y)}) - Ningún elemento seleccionado")
            self.drag_start = None
        
        self._update_display()
    
    def on_canvas_drag(self, event):
        """Maneja el arrastre en el canvas."""
        if not self.edit_mode or not self.drag_start or not self.pdf_editor.selected_element:
            return
        
        canvas_x = self.canvas.canvasx(event.x) - 10
        canvas_y = self.canvas.canvasy(event.y) - 10
        
        # Calcular desplazamiento
        dx = canvas_x - self.drag_start[0]
        dy = canvas_y - self.drag_start[1]
        
        # Mover el elemento seleccionado
        if self.pdf_editor.move_selected_element(dx, dy):
            self.drag_start = (canvas_x, canvas_y)
            self._update_display()
            self.update_status(f"Moviendo elemento: Δx={int(dx)}, Δy={int(dy)}")
        self.dragging = True
    
    def on_canvas_release(self, event):
        """Maneja la liberación del mouse."""
        if self.dragging:
            self.update_status("Elemento soltado")
            self.dragging = False
        self.drag_start = None
    
    def on_canvas_double_click(self, event):
        """Maneja doble clic en el canvas para editar elementos."""
        if not self.edit_mode or not self.pdf_editor.current_pdf:
            return
        
        canvas_x = self.canvas.canvasx(event.x) - 10
        canvas_y = self.canvas.canvasy(event.y) - 10
        
        # Seleccionar elemento en la posición
        selected = self.pdf_editor.select_element_at_position(self.current_page, (canvas_x, canvas_y))
        
        if selected and selected.type == 'text':
            # Mostrar diálogo para editar texto
            new_text = show_text_input(
                self.root,
                "Editar Texto",
                "Modifique el texto:",
                selected.content
            )
            
            if new_text and new_text != selected.content:
                if self.pdf_editor.edit_selected_element({'content': new_text}):
                    self._update_display()
                    self.update_status(f"Texto editado: '{new_text[:30]}...'")
                    messagebox.showinfo("Éxito", "Texto editado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo editar el texto")
        else:
            self.update_status(f"Doble clic en: ({int(canvas_x)}, {int(canvas_y)}) - No hay texto para editar")
    
    def on_canvas_key(self, event):
        """Maneja teclas presionadas."""
        if not self.edit_mode:
            return
        
        if event.keysym == 'Delete' and self.pdf_editor.selected_element:
            # Confirmar eliminación
            element = self.pdf_editor.selected_element
            element_desc = f"texto '{element.content[:30]}...'" if element.type == 'text' else "imagen"
            
            if messagebox.askyesno("Confirmar eliminación", f"¿Está seguro de que desea eliminar el {element_desc}?"):
                if self.pdf_editor.delete_selected_element():
                    self._update_display()
                    self.update_status(f"Elemento eliminado: {element_desc}")
                    messagebox.showinfo("Éxito", "Elemento eliminado correctamente")
                else:
                    messagebox.showerror("Error", "No se pudo eliminar el elemento")
        elif event.keysym == 'Escape':
            # Deseleccionar elemento
            self.pdf_editor.clear_selection()
            self._update_display()
            self.update_status("Selección cancelada")
    
    def on_mouse_wheel(self, event):
        """Maneja el scroll del mouse."""
        # Scroll vertical
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")