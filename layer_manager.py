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
from qgis.core import (
    QgsVectorLayer, QgsField, QgsProject, 
    QgsEditFormConfig, QgsAttributeEditorContainer, QgsAttributeEditorField
)
from PyQt5.QtCore import QVariant

class LayerManager:
    def __init__(self):
        # We will append these pollutant fields to every layer
        self.pollutants = ['SO2', 'NO2', 'PM10', 'PM2.5', 'CO', 'Pb', 'OTHER']
        
        # Base aliases (labels with units) that apply to ALL source types
        self.base_aliases = {
            "source_id": "Source ID",
            "description": "Description",
            "elevation": "Base Elevation (m)",
            "release_height": "Release Height (m)",
            "szinit": "Initial Sigma-Z (m)"
        }
        
        # Automatically append (g/s) to all pollutants
        for p in self.pollutants:
            self.base_aliases[p] = f"{p} Emission (g/s)"

    def _get_pollutant_fields(self):
        """Helper to generate QgsFields for all pollutants."""
        return [QgsField(p, QVariant.Double) for p in self.pollutants]

    def _format_form(self, layer, param_fields, specific_aliases):
        """Applies Aliases (Units) and organizes the QGIS Form into Group Boxes."""
        
        # 1. Apply Aliases (Updates the visible labels)
        aliases = self.base_aliases.copy()
        aliases.update(specific_aliases)
        
        for field_name, alias in aliases.items():
            idx = layer.fields().indexOf(field_name)
            if idx != -1:
                layer.setFieldAlias(idx, alias)

        # 2. Tidy the Layout (Makes the window taller and beautifully sectioned)
        config = layer.editFormConfig()
        config.setLayout(QgsEditFormConfig.TabLayout)
        root = config.invisibleRootContainer()
        
        # --- THE FIX: Clear the default auto-generated flat list first! ---
        root.clear()
        # ------------------------------------------------------------------
        
        # Box 1: Identification
        grp_id = QgsAttributeEditorContainer("1. Identification", root)
        grp_id.setIsGroupBox(True)
        grp_id.addChildElement(QgsAttributeEditorField("source_id", layer.fields().indexOf("source_id"), grp_id))
        grp_id.addChildElement(QgsAttributeEditorField("description", layer.fields().indexOf("description"), grp_id))
        root.addChildElement(grp_id)
        
        # Box 2: Physical Parameters
        grp_params = QgsAttributeEditorContainer("2. Physical Parameters", root)
        grp_params.setIsGroupBox(True)
        for f in param_fields:
            idx = layer.fields().indexOf(f)
            grp_params.addChildElement(QgsAttributeEditorField(f, idx, grp_params))
        root.addChildElement(grp_params)
        
        # Box 3: Emission Rates (g/s)
        grp_em = QgsAttributeEditorContainer("3. Emission Rates (g/s)", root)
        grp_em.setIsGroupBox(True)
        for p in self.pollutants:
            idx = layer.fields().indexOf(p)
            grp_em.addChildElement(QgsAttributeEditorField(p, idx, grp_em))
        root.addChildElement(grp_em)
        
        # Apply the configuration to the layer
        layer.setEditFormConfig(config)

    def create_point_layer(self):
        """Creates the ATAQ Point Sources layer."""
        layer = QgsVectorLayer("Point?crs=EPSG:4326", "ATAQ_Point_Sources", "memory")
        provider = layer.dataProvider()
        
        fields = [
            QgsField("source_id", QVariant.String),
            QgsField("elevation", QVariant.Double),
            QgsField("stack_height", QVariant.Double),
            QgsField("stack_temp_k", QVariant.Double),
            QgsField("stack_velocity", QVariant.Double),
            QgsField("stack_diameter", QVariant.Double),
            QgsField("description", QVariant.String)
        ] + self._get_pollutant_fields()
        
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Apply Formatting
        self._format_form(
            layer, 
            param_fields=["elevation", "stack_height", "stack_temp_k", "stack_velocity", "stack_diameter"],
            specific_aliases={
                "stack_height": "Stack Height (m)",
                "stack_temp_k": "Temperature (K)",
                "stack_velocity": "Velocity (m/s)",
                "stack_diameter": "Diameter (m)"
            }
        )
        
        QgsProject.instance().addMapLayer(layer)
        return layer

    def create_line_layer(self):
        """Creates the ATAQ Line Sources layer."""
        layer = QgsVectorLayer("LineString?crs=EPSG:4326", "ATAQ_Line_Sources", "memory")
        provider = layer.dataProvider()
        
        fields = [
            QgsField("source_id", QVariant.String),
            QgsField("elevation", QVariant.Double),
            QgsField("release_height", QVariant.Double),
            QgsField("width_m", QVariant.Double),
            QgsField("szinit", QVariant.Double),
            QgsField("description", QVariant.String)
        ] + self._get_pollutant_fields()
        
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Apply Formatting
        self._format_form(
            layer, 
            param_fields=["elevation", "release_height", "width_m", "szinit"],
            specific_aliases={"width_m": "Width (m)"}
        )
        
        QgsProject.instance().addMapLayer(layer)
        return layer

    def create_area_layer(self):
        """Creates the ATAQ Area Sources layer (True Polygons)."""
        layer = QgsVectorLayer("Polygon?crs=EPSG:4326", "ATAQ_Area_Sources", "memory")
        provider = layer.dataProvider()
        
        fields = [
            QgsField("source_id", QVariant.String),
            QgsField("elevation", QVariant.Double),
            QgsField("release_height", QVariant.Double),
            QgsField("szinit", QVariant.Double),
            QgsField("description", QVariant.String)
        ] + self._get_pollutant_fields()
        
        provider.addAttributes(fields)
        layer.updateFields()
        
        # Apply Formatting
        self._format_form(
            layer, 
            param_fields=["elevation", "release_height", "szinit"],
            specific_aliases={}
        )
        
        QgsProject.instance().addMapLayer(layer)
        return layer

    def initialize_all_layers(self):
        """Utility to safely generate all three layers at once."""
        self.create_point_layer()
        self.create_line_layer()
        self.create_area_layer()
