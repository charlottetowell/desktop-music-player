"""
Icon utility for loading and managing SVG icons
"""

from pathlib import Path
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtCore import QSize, Qt

# Base icon directory
ICON_DIR = Path(__file__).parent.parent.parent / "assets" / "icons" / "svg"


class IconManager:
    """Centralized icon management for the application."""
    
    _cache = {}
    
    @staticmethod
    def get_icon(name: str, category: str = "") -> QIcon:
        """
        Load an SVG icon by name.
        
        Args:
            name: Icon filename without extension (e.g., 'play', 'pause')
            category: Optional subdirectory (e.g., 'controls', 'media', 'navigation')
            
        Returns:
            QIcon object
        """
        cache_key = f"{category}/{name}" if category else name
        
        if cache_key in IconManager._cache:
            return IconManager._cache[cache_key]
        
        # Construct path
        if category:
            icon_path = ICON_DIR / category / f"{name}.svg"
        else:
            icon_path = ICON_DIR / f"{name}.svg"
        
        if icon_path.exists():
            icon = QIcon(str(icon_path))
            IconManager._cache[cache_key] = icon
            return icon
        else:
            print(f"Warning: Icon not found: {icon_path}")
            return QIcon()
    
    @staticmethod
    def get_pixmap(name: str, size: int = 24, category: str = "") -> QPixmap:
        """
        Load an SVG icon as a pixmap with specific size.
        
        Args:
            name: Icon filename without extension
            size: Desired size in pixels (default: 24)
            category: Optional subdirectory
            
        Returns:
            QPixmap object
        """
        if category:
            icon_path = ICON_DIR / category / f"{name}.svg"
        else:
            icon_path = ICON_DIR / f"{name}.svg"
        
        if icon_path.exists():
            renderer = QSvgRenderer(str(icon_path))
            pixmap = QPixmap(QSize(size, size))
            pixmap.fill(Qt.transparent)
            renderer.render(pixmap)
            return pixmap
        else:
            print(f"Warning: Icon not found: {icon_path}")
            return QPixmap()
    
    @staticmethod
    def clear_cache() -> None:
        """Clear the icon cache."""
        IconManager._cache.clear()


# Convenience functions
def load_icon(name: str, category: str = "") -> QIcon:
    """Convenience function to load an icon."""
    return IconManager.get_icon(name, category)


def load_pixmap(name: str, size: int = 24, category: str = "") -> QPixmap:
    """Convenience function to load an icon as pixmap."""
    return IconManager.get_pixmap(name, size, category)
