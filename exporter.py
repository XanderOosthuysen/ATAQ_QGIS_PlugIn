"""
ATAQ QGIS Plugin
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
import csv
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox

class AtaqExporter:
    def __init__(self, iface):
        self.iface = iface
        
        # Define the layers and their target filenames
        self.layer_map = {
            "ATAQ_Point_Sources": "point_sources.csv",
            "ATAQ_Line_Sources": "line_sources.csv",
            "ATAQ_Area_Sources": "area_sources.csv"
        }

    def export_layers(self):
        """Finds the ATAQ layers and exports them to a selected folder."""
        # 1. Ask the user where to save the CSVs
        export_dir = QFileDialog.getExistingDirectory(
            self.iface.mainWindow(),
            "Select ATAQ Inventory Folder",
            ""
        )
        
        # If the user cancels the dialog, abort gracefully
        if not export_dir:
            return

        exported_files = []
        errors = []

        # 2. Process each layer
        for layer_name, filename in self.layer_map.items():
            # Find the layer in the QGIS project
            layers = QgsProject.instance().mapLayersByName(layer_name)
            
            if not layers:
                continue # Layer doesn't exist, skip it
                
            layer = layers[0]
            
            # If the layer is empty, skip it
            if layer.featureCount() == 0:
                continue

            # 3. Write the CSV
            filepath = os.path.join(export_dir, filename)
            try:
                with open(filepath, 'w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    
                    # Get field names and inject 'WKT' right after 'source_id'
                    field_names = [field.name() for field in layer.fields()]
                    headers = ["source_id", "WKT"] + field_names[1:]
                    writer.writerow(headers)
                    
                    # Loop through all drawn features
                    for feat in layer.getFeatures():
                        # Extract the geometry and convert to WKT text string
                        geom = feat.geometry()
                        wkt_str = geom.asWkt() if geom else "GEOMETRY_ERROR"
                        
                        # Extract the attributes
                        attrs = feat.attributes()
                        
                        # Build the row (ID, WKT, ...everything else)
                        row = [attrs[0], wkt_str] + attrs[1:]
                        writer.writerow(row)
                        
                exported_files.append(filename)
                
            except Exception as e:
                errors.append(f"Failed to write {filename}: {str(e)}")

        # 4. Notify the user of the result
        if errors:
            QMessageBox.critical(self.iface.mainWindow(), "Export Errors", "\n".join(errors))
        elif exported_files:
            self.iface.messageBar().pushMessage(
                "ATAQ Exporter", 
                f"Successfully exported: {', '.join(exported_files)}", 
                level=0, duration=5
            )
        else:
            self.iface.messageBar().pushMessage(
                "ATAQ Exporter", 
                "No features to export. Draw some sources first!", 
                level=1, duration=5
            )
