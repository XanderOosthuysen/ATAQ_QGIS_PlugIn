"""
ATAQ AERMOD Pipeline
Copyright (C) 2026 ATAQ

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
