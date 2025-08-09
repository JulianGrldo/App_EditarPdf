"""Paleta de colores para la aplicación Editor de PDF.

Esta paleta está diseñada con tonos azules para transmitir tranquilidad y profesionalismo.
"""

class ColorPalette:
    """Paleta de colores principal de la aplicación."""
    
    # Colores principales
    PRIMARY_BLUE = "#2E86AB"      # Azul principal - botones principales
    SECONDARY_BLUE = "#A8DADC"    # Azul secundario - elementos secundarios
    LIGHT_BLUE = "#F1FAEE"       # Azul muy claro - fondo de paneles
    DARK_BLUE = "#1D3557"        # Azul oscuro - texto principal
    ACCENT_BLUE = "#457B9D"       # Azul de acento - hover y selección
    
    # Colores de fondo
    BACKGROUND = "#F8FBFF"        # Fondo principal
    CARD_BACKGROUND = "#FFFFFF"   # Fondo de tarjetas
    SIDEBAR_BACKGROUND = "#E8F4F8" # Fondo de barra lateral
    
    # Colores de texto
    TEXT_PRIMARY = "#1D3557"      # Texto principal
    TEXT_SECONDARY = "#457B9D"    # Texto secundario
    TEXT_LIGHT = "#6C757D"       # Texto claro
    TEXT_WHITE = "#FFFFFF"       # Texto blanco
    
    # Colores de estado
    SUCCESS = "#28A745"           # Verde para éxito
    WARNING = "#FFC107"           # Amarillo para advertencias
    ERROR = "#DC3545"             # Rojo para errores
    INFO = "#17A2B8"              # Azul info
    
    # Colores de botones
    BUTTON_PRIMARY = PRIMARY_BLUE
    BUTTON_PRIMARY_HOVER = "#1E5F7A"
    BUTTON_SECONDARY = SECONDARY_BLUE
    BUTTON_SECONDARY_HOVER = "#8BC5C8"
    BUTTON_DANGER = ERROR
    BUTTON_DANGER_HOVER = "#C82333"
    
    # Colores de bordes
    BORDER_LIGHT = "#DEE2E6"
    BORDER_MEDIUM = "#CED4DA"
    BORDER_DARK = "#6C757D"
    
    @classmethod
    def get_gradient_colors(cls):
        """Retorna colores para gradientes."""
        return {
            'primary_gradient': [cls.PRIMARY_BLUE, cls.ACCENT_BLUE],
            'light_gradient': [cls.LIGHT_BLUE, cls.SECONDARY_BLUE],
            'dark_gradient': [cls.DARK_BLUE, cls.PRIMARY_BLUE]
        }
    
    @classmethod
    def get_theme_colors(cls):
        """Retorna un diccionario con todos los colores del tema."""
        return {
            'primary': cls.PRIMARY_BLUE,
            'secondary': cls.SECONDARY_BLUE,
            'background': cls.BACKGROUND,
            'surface': cls.CARD_BACKGROUND,
            'text_primary': cls.TEXT_PRIMARY,
            'text_secondary': cls.TEXT_SECONDARY,
            'accent': cls.ACCENT_BLUE
        }