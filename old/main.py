import json
import struct

import ifcopenshell
import ifcopenshell.geom
import psycopg2


class IFCExport:
    def __init__(self, path, db_config):
        """Initialize with IFC file path and database configuration."""
        self.path = path
        self.db_config = db_config  # Dictionary with database connection details
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(
            self.settings.USE_WORLD_COORDS, True
        )  # Use global coordinates

    def load_ifc_file(self):
        """Load the IFC file."""
        return ifcopenshell.open(self.path)

    def select_POI(self, ifc_file):
        """Select points of interest (e.g., walls and similar elements)."""
        return (
            ifc_file.by_type("IfcWall")
            + ifc_file.by_type("IfcWallStandardCase")
            + ifc_file.by_type("IfcCurtainWall")
            + ifc_file.by_type("IfcBuildingElementPart")
        )

    def mesh_to_stl_binary(self, vertices, faces):
        """Convert mesh vertices and faces to STL binary format."""
        num_triangles = len(faces) // 3
        stl_data = bytearray()
        stl_data += b"\0" * 80  # 80-byte header
        stl_data += struct.pack("<I", num_triangles)  # Number of triangles
        for i in range(0, len(faces), 3):
            # Normal (placeholder, can be computed if needed)
            stl_data += struct.pack("<fff", 0.0, 0.0, 0.0)
            # Vertex 1
            v1 = faces[i] * 3
            stl_data += struct.pack(
                "<fff", vertices[v1], vertices[v1 + 1], vertices[v1 + 2]
            )
            # Vertex 2
            v2 = faces[i + 1] * 3
            stl_data += struct.pack(
                "<fff", vertices[v2], vertices[v2 + 1], vertices[v2 + 2]
            )
            # Vertex 3
            v3 = faces[i + 2] * 3
            stl_data += struct.pack(
                "<fff", vertices[v3], vertices[v3 + 1], vertices[v3 + 2]
            )
            # Attribute byte count
            stl_data += b"\0\0"
        return stl_data

    def store_in_database(self, ifc_id, stl_binary, metadata):
        """Store element data in PostgreSQL."""
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        # Store IFC ID, geometry (BYTEA), and metadata (JSONB)
        cur.execute(
            "INSERT INTO elements (ifc_id, geometry, metadata) VALUES (%s, %s, %s)",
            (ifc_id, psycopg2.Binary(stl_binary), json.dumps(metadata)),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_metadata(self, elements):
        """Extract geometry and metadata for each element and store it."""
        for element in elements:
            try:
                # Extract geometry
                shape = ifcopenshell.geom.create_shape(self.settings, element)
                geometry = shape.geometry
                vertices = geometry.verts
                faces = geometry.faces
                # vertices = shape.verts  # List of vertex coordinates
                # faces = shape.faces  # List of face indices

                # -------
                print(shape.geometry, "\n")
                print(faces, "\n")
                print(vertices, "\n")
                break

                # ------
                stl_binary = self.mesh_to_stl_binary(vertices, faces)

                # Extract metadata (e.g., ArchiCADProperties)
                archicad_props = {}
                for rel in element.IsDefinedBy:
                    if rel.is_a("IfcRelDefinesByProperties"):
                        pset = rel.RelatingPropertyDefinition
                        if (
                            pset
                            and pset.is_a("IfcPropertySet")
                            and pset.Name == "ArchiCADProperties"
                        ):
                            for prop in pset.HasProperties:
                                if (
                                    prop.is_a("IfcPropertySingleValue")
                                    and prop.NominalValue
                                ):
                                    archicad_props[prop.Name] = (
                                        prop.NominalValue.wrappedValue
                                    )

                # Compile metadata
                metadata = {
                    "Ursprungsgeschoss Name": archicad_props.get(
                        "Ursprungsgeschoss Name", "N/A"
                    ),
                    "Ursprungsgeschoss Nummer": archicad_props.get(
                        "Ursprungsgeschoss Nummer", "N/A"
                    ),
                    "ElementType": element.is_a(),
                }

                # Store in database
                self.store_in_database(element.GlobalId, stl_binary, metadata)
            except Exception as e:
                print(f"Error processing {element.GlobalId}: {e}")

    def run(self):
        """Execute the export process."""
        ifc_file = self.load_ifc_file()
        elements = self.select_POI(ifc_file)
        self.get_metadata(elements)


if __name__ == "__main__":
    # Example usage
    path = "ifc_files/original_bim.ifc"
    db_config = {
        "dbname": "ifc",
        "user": "postgres",
        # "password": "your_password",
        "host": "localhost",
    }
    ifc_exporter = IFCExport(path, db_config)
    ifc_exporter.run()
