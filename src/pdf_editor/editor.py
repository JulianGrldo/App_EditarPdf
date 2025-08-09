"""Módulo principal para la edición de archivos PDF.

Este módulo contiene la clase PDFEditor que maneja todas las operaciones
de edición de archivos PDF como rotación, fusión, extracción, etc.
"""

import os
import fitz  # PyMuPDF
from PyPDF2 import PdfReader, PdfWriter
from typing import List, Optional, Tuple
from pathlib import Path


class PDFEditor:
    """Clase principal para editar archivos PDF."""
    
    def __init__(self):
        """Inicializa el editor de PDF."""
        self.current_pdf = None
        self.current_path = None
        self.pages_info = []
    
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