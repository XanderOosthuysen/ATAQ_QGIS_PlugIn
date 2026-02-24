"""
ataq_plugin.py
Main entry point for the ATAQ QGIS Plugin.
"""
import os
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .layer_manager import LayerManager
from .exporter import AtaqExporter  # <-- NEW IMPORT

class AtaqPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.init_action = None
        self.export_action = None # <-- NEW ACTION

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, 'icon.png')
        
        # --- BUTTON 1: Initialize Layers ---
        self.init_action = QAction(QIcon(icon_path), "1. Initialize ATAQ Layers", self.iface.mainWindow())
        self.init_action.triggered.connect(self.run_init)
        self.iface.addToolBarIcon(self.init_action)
        self.iface.addPluginToMenu("&ATAQ Exporter", self.init_action)

        # --- BUTTON 2: Export Inventory ---
        # (You can use the same icon for now, or add an 'export_icon.png' later)
        self.export_action = QAction(QIcon(icon_path), "2. Export Inventory", self.iface.mainWindow())
        self.export_action.triggered.connect(self.run_export)
        self.iface.addToolBarIcon(self.export_action)
        self.iface.addPluginToMenu("&ATAQ Exporter", self.export_action)

    def unload(self):
        if self.init_action:
            self.iface.removePluginMenu("&ATAQ Exporter", self.init_action)
            self.iface.removeToolBarIcon(self.init_action)
        if self.export_action:
            self.iface.removePluginMenu("&ATAQ Exporter", self.export_action)
            self.iface.removeToolBarIcon(self.export_action)

    def run_init(self):
        manager = LayerManager()
        manager.initialize_all_layers()
        self.iface.messageBar().pushMessage(
            "ATAQ Exporter", "Successfully initialized Memory layers!", level=0, duration=5)

    def run_export(self):
        """Triggers the new exporter logic."""
        exporter = AtaqExporter(self.iface)
        exporter.export_layers()
