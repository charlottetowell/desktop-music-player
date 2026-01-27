"""
Font management for the application
Handles loading and caching of custom fonts
"""

from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtCore import QFile
import os
from pathlib import Path


class FontManager:
    """Manages custom font loading and provides font instances."""
    
    _instance = None
    _fonts_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Don't load fonts immediately - wait for explicit call
        pass
    
    def load_fonts(self) -> None:
        """Load custom fonts from assets directory. Must be called after QApplication init."""
        if FontManager._fonts_loaded:
            return
            
        font_dir = Path(__file__).parent.parent.parent / "assets" / "fonts"
        
        if font_dir.exists():
            for font_file in font_dir.glob("*.ttf"):
                font_id = QFontDatabase.addApplicationFont(str(font_file))
                if font_id != -1:
                    families = QFontDatabase.applicationFontFamilies(font_id)
                    print(f"Loaded font: {families}")
        
        FontManager._fonts_loaded = True
    
    @staticmethod
    def get_font(size: int = 12, weight: QFont.Weight = QFont.Normal) -> QFont:
        """
        Get Jersey 25 font with specified size and weight.
        Falls back to system default if Jersey 25 is unavailable.
        """
        font = QFont("Jersey 25", size, weight)
        
        # Check if Jersey 25 is available, otherwise try fallbacks
        if font.family() != "Jersey 25":
            # Try common fallbacks
            for fallback in ["Jersey 25 Charted", "Impact", "Arial Black", "Arial"]:
                font = QFont(fallback, size, weight)
                if font.family() == fallback:
                    break
        
        return font
    
    @staticmethod
    def get_display_font(size: int = 24) -> QFont:
        """Get large display font for headers."""
        return FontManager.get_font(size, QFont.Bold)
    
    @staticmethod
    def get_title_font(size: int = 16) -> QFont:
        """Get title font for section headers."""
        return FontManager.get_font(size, QFont.Bold)
    
    @staticmethod
    def get_body_font(size: int = 12) -> QFont:
        """Get body font for regular text."""
        return FontManager.get_font(size, QFont.Normal)
    
    @staticmethod
    def get_small_font(size: int = 10) -> QFont:
        """Get small font for secondary text."""
        return FontManager.get_font(size, QFont.Normal)


# Singleton instance (lazy initialization)
font_manager = FontManager()
