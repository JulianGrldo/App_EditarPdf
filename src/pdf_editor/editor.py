"""Módulo principal para la edición de archivos PDF.

Este módulo contiene la clase PDFEditor que maneja todas las operaciones
de edición de archivos PDF como rotación, fusión, extracción, etc.
"""

import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageTk
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfutils
from reportlab.lib.colors import black
import io
import json
from typing import List, Optional, Tuple, Dict
from pathlib import Path


class PDFElement:
    """Representa un elemento editable en el PDF."""
    
    def __init__(self, element_type: str, content: str, position: Tuple[float, float], 
                 size: Tuple[float, float] = (100, 20), font_size: int = 12, color: str = "black"):
        self.id = id(self)  # ID único
        self.type = element_type  # 'text', 'image'
        self.content = content
        self.position = position  # (x, y)
        self.size = size  # (width, height)
        self.font_size = font_size
        self.color = color
        self.selected = False
        self.page_number = 0
    
    def to_dict(self) -> Dict:
        """Convierte el elemento a diccionario para serialización."""
        return {
            'id': self.id,
            'type': self.type,
            'content': self.content,
            'position': self.position,
            'size': self.size,
            'font_size': self.font_size,
            'color': self.color,
            'page_number': self.page_number
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Crea un elemento desde un diccionario."""
        element = cls(
            data['type'],
            data['content'],
            tuple(data['position']),
            tuple(data['size']),
            data['font_size'],
            data['color']
        )
        element.id = data['id']
        element.page_number = data['page_number']
        return element


class PDFEditor:
    """Clase principal para editar archivos PDF."""
    
    def __init__(self):
        """Inicializa el editor de PDF."""
        self.current_pdf = None
        self.current_path = None
        self.pages_info = []
        self.elements = {}  # {page_number: [PDFElement, ...]}
        self.selected_element = None
        self.edit_mode = False
    
    def load_pdf(self, file_path: str) -> bool:
        """Carga un archivo PDF para edición.
        
        Args:
            file_path: Ruta al archivo PDF
            
        Returns:
            True si se cargó correctamente, False en caso contrario
        """
        try:
            self.current_pdf = fitz.open(file_path)
            self.current_path = file_path
            self._update_pages_info()
            return True
        except Exception as e:
            print(f"Error al cargar PDF: {e}")
            return False
    
    def _update_pages_info(self):
        """Actualiza la información de las páginas del PDF actual."""
        if not self.current_pdf:
            return
        
        self.pages_info = []
        for page_num in range(len(self.current_pdf)):
            page = self.current_pdf[page_num]
            info = {
                'number': page_num + 1,
                'width': page.rect.width,
                'height': page.rect.height,
                'rotation': page.rotation
            }
            self.pages_info.append(info)
    
    def get_page_count(self) -> int:
        """Retorna el número de páginas del PDF actual."""
        return len(self.current_pdf) if self.current_pdf else 0
    
    def get_page_image(self, page_num: int, zoom: float = 1.0) -> Optional[bytes]:
        """Obtiene una imagen de la página especificada.
        
        Args:
            page_num: Número de página (0-indexado)
            zoom: Factor de zoom para la imagen
            
        Returns:
            Bytes de la imagen PNG o None si hay error
        """
        if not self.current_pdf or page_num >= len(self.current_pdf):
            return None
        
        try:
            page = self.current_pdf[page_num]
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            return pix.tobytes("png")
        except Exception as e:
            print(f"Error al obtener imagen de página: {e}")
            return None
    
    def rotate_page(self, page_num: int, angle: int) -> bool:
        """Rota una página específica.
        
        Args:
            page_num: Número de página (0-indexado)
            angle: Ángulo de rotación (90, 180, 270)
            
        Returns:
            True si se rotó correctamente
        """
        if not self.current_pdf or page_num >= len(self.current_pdf):
            return False
        
        try:
            page = self.current_pdf[page_num]
            page.set_rotation(angle)
            self._update_pages_info()
            return True
        except Exception as e:
            print(f"Error al rotar página: {e}")
            return False
    
    def extract_pages(self, page_numbers: List[int], output_path: str) -> bool:
        """Extrae páginas específicas a un nuevo PDF.
        
        Args:
            page_numbers: Lista de números de página (0-indexados)
            output_path: Ruta del archivo de salida
            
        Returns:
            True si se extrajo correctamente
        """
        if not self.current_pdf:
            return False
        
        try:
            new_pdf = fitz.open()
            for page_num in page_numbers:
                if page_num < len(self.current_pdf):
                    new_pdf.insert_pdf(self.current_pdf, from_page=page_num, to_page=page_num)
            
            new_pdf.save(output_path)
            new_pdf.close()
            return True
        except Exception as e:
            print(f"Error al extraer páginas: {e}")
            return False
    
    def merge_pdfs(self, pdf_paths: List[str], output_path: str) -> bool:
        """Fusiona múltiples PDFs en uno solo.
        
        Args:
            pdf_paths: Lista de rutas de archivos PDF
            output_path: Ruta del archivo de salida
            
        Returns:
            True si se fusionó correctamente
        """
        try:
            merged_pdf = fitz.open()
            
            for pdf_path in pdf_paths:
                if os.path.exists(pdf_path):
                    pdf_doc = fitz.open(pdf_path)
                    merged_pdf.insert_pdf(pdf_doc)
                    pdf_doc.close()
            
            merged_pdf.save(output_path)
            merged_pdf.close()
            return True
        except Exception as e:
            print(f"Error al fusionar PDFs: {e}")
            return False
    
    def add_text_element(self, page_number: int, text: str, position: Tuple[float, float], 
                        font_size: int = 12, color: str = "black") -> PDFElement:
        """Añade un elemento de texto editable a una página específica."""
        element = PDFElement('text', text, position, (len(text) * font_size * 0.6, font_size), font_size, color)
        element.page_number = page_number
        
        if page_number not in self.elements:
            self.elements[page_number] = []
        
        self.elements[page_number].append(element)
        return element
    
    def add_image_element(self, page_number: int, image_path: str, position: Tuple[float, float], 
                         size: Tuple[float, float] = (100, 100)) -> PDFElement:
        """Añade un elemento de imagen editable a una página específica."""
        element = PDFElement('image', image_path, position, size)
        element.page_number = page_number
        
        if page_number not in self.elements:
            self.elements[page_number] = []
        
        self.elements[page_number].append(element)
        return element
    
    def select_element_at_position(self, page_number: int, position: Tuple[float, float]) -> Optional[PDFElement]:
        """Selecciona un elemento en la posición especificada."""
        if page_number not in self.elements:
            return None
        
        # Deseleccionar elemento actual
        if self.selected_element:
            self.selected_element.selected = False
        
        # Buscar elemento en la posición (en orden inverso para seleccionar el más reciente)
        for element in reversed(self.elements[page_number]):
            x, y = element.position
            w, h = element.size
            
            if (x <= position[0] <= x + w and y <= position[1] <= y + h):
                element.selected = True
                self.selected_element = element
                return element
        
        self.selected_element = None
        return None
    
    def move_selected_element(self, dx: float, dy: float) -> bool:
        """Mueve el elemento seleccionado por un desplazamiento relativo."""
        if self.selected_element:
            current_x, current_y = self.selected_element.position
            self.selected_element.position = (current_x + dx, current_y + dy)
            return True
        return False
    
    def edit_selected_element(self, new_content: str) -> bool:
        """Edita el contenido del elemento seleccionado."""
        if self.selected_element and self.selected_element.type == 'text':
            self.selected_element.content = new_content
            # Ajustar tamaño basado en el nuevo contenido
            font_size = self.selected_element.font_size
            self.selected_element.size = (len(new_content) * font_size * 0.6, font_size)
            return True
        return False
    
    def delete_selected_element(self) -> bool:
        """Elimina el elemento seleccionado."""
        if self.selected_element:
            page_number = self.selected_element.page_number
            if page_number in self.elements:
                self.elements[page_number].remove(self.selected_element)
                self.selected_element = None
                return True
        return False
    
    def get_page_elements(self, page_number: int) -> List[PDFElement]:
        """Obtiene todos los elementos de una página."""
        return self.elements.get(page_number, [])
    
    def clear_selection(self):
        """Deselecciona el elemento actual."""
        if self.selected_element:
            self.selected_element.selected = False
            self.selected_element = None
    
    def add_text(self, page_num: int, text: str, position: Tuple[float, float], 
                 font_size: int = 12, color: Tuple[float, float, float] = (0, 0, 0)) -> bool:
        """Añade texto a una página específica.
        
        Args:
            page_num: Número de página (0-indexado)
            text: Texto a añadir
            position: Posición (x, y) donde añadir el texto
            font_size: Tamaño de la fuente
            color: Color del texto en RGB (0-1)
            
        Returns:
            True si se añadió correctamente
        """
        if not self.current_pdf or page_num >= len(self.current_pdf):
            return False
        
        try:
            page = self.current_pdf[page_num]
            point = fitz.Point(position[0], position[1])
            page.insert_text(point, text, fontsize=font_size, color=color)
            return True
        except Exception as e:
            print(f"Error al añadir texto: {e}")
            return False
    
    def save_pdf(self, output_path: Optional[str] = None) -> bool:
        """Guarda el PDF actual.
        
        Args:
            output_path: Ruta de salida (opcional, usa la ruta actual si no se especifica)
            
        Returns:
            True si se guardó correctamente
        """
        if not self.current_pdf:
            return False
        
        try:
            save_path = output_path or self.current_path
            self.current_pdf.save(save_path)
            return True
        except Exception as e:
            print(f"Error al guardar PDF: {e}")
            return False
    
    def close_pdf(self):
        """Cierra el PDF actual y libera recursos."""
        if self.current_pdf:
            self.current_pdf.close()
            self.current_pdf = None
            self.current_path = None
            self.pages_info = []
    
    def get_pdf_info(self) -> dict:
        """Obtiene información del PDF actual.
        
        Returns:
            Diccionario con información del PDF
        """
        if not self.current_pdf:
            return {}
        
        metadata = self.current_pdf.metadata
        return {
            'title': metadata.get('title', 'Sin título'),
            'author': metadata.get('author', 'Desconocido'),
            'subject': metadata.get('subject', ''),
            'creator': metadata.get('creator', ''),
            'producer': metadata.get('producer', ''),
            'creation_date': metadata.get('creationDate', ''),
            'modification_date': metadata.get('modDate', ''),
            'page_count': len(self.current_pdf),
            'file_size': os.path.getsize(self.current_path) if self.current_path else 0
        }