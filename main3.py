import json

import ifcopenshell
import ifcopenshell.geom
import psycopg2


class IFCExport:
    def __init__(self, path, db_config):
        """Initialize with IFC file path and database configuration."""
        self.path = path
        self.db_config = db_config
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_WORLD_COORDS, True)

    def load_ifc_file(self):
        return ifcopenshell.open(self.path)

    def select_POI(self, ifc_file):
        return (
            ifc_file.by_type("IfcWall")
            + ifc_file.by_type("IfcWallStandardCase")
            + ifc_file.by_type("IfcCurtainWall")
            + ifc_file.by_type("IfcBuildingElementPart")
        )

    def mesh_to_geojson_polygons(self, vertices, faces):
        """
        Convert vertices and faces to GeoJSON FeatureCollection of triangles (polygons).
        vertices: flat list of floats [x0,y0,z0, x1,y1,z1, ...]
        faces: flat list of vertex indices [i0, i1, i2, i3, i4, i5, ...], each triple is a triangle
        """
        features = []

        # Each face is 3 indices into vertices
        for i in range(0, len(faces), 3):
            idx1, idx2, idx3 = faces[i], faces[i + 1], faces[i + 2]

            # Extract coordinates of each vertex (x, y, z)
            v1 = vertices[idx1 * 3 : idx1 * 3 + 3]
            v2 = vertices[idx2 * 3 : idx2 * 3 + 3]
            v3 = vertices[idx3 * 3 : idx3 * 3 + 3]

            # Polygon coordinates must be closed (first = last)
            polygon_coords = [v1, v2, v3, v1]

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords],
                },
                "properties": {},
            }
            features.append(feature)

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }
        return geojson

    def store_in_database(self, ifc_id, geojson_geom, metadata):
        conn = psycopg2.connect(**self.db_config)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO elements (ifc_id, geometry, metadata) VALUES (%s, %s::jsonb, %s::jsonb)",
            (ifc_id, json.dumps(geojson_geom), json.dumps(metadata)),
        )
        conn.commit()
        cur.close()
        conn.close()

    def get_metadata(self, elements):
        for element in elements:
            try:
                shape = ifcopenshell.geom.create_shape(self.settings, element)
                geometry = shape.geometry
                vertices = geometry.verts
                faces = geometry.faces

                if not vertices or not faces:
                    print(f"No geometry for element {element.GlobalId}")
                    continue

                geojson_geom = self.mesh_to_geojson_polygons(vertices, faces)

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

                metadata = {
                    "Ursprungsgeschoss Name": archicad_props.get(
                        "Ursprungsgeschoss Name", "N/A"
                    ),
                    "Ursprungsgeschoss Nummer": archicad_props.get(
                        "Ursprungsgeschoss Nummer", "N/A"
                    ),
                    "ElementType": element.is_a(),
                }

                self.store_in_database(element.GlobalId, geojson_geom, metadata)
                print(
                    f"Stored element {element.GlobalId} with {len(faces)//3} triangles."
                )

            except Exception as e:
                print(f"Error processing {element.GlobalId}: {e}")

    def run(self):
        ifc_file = self.load_ifc_file()
        elements = self.select_POI(ifc_file)
        self.get_metadata(elements)


if __name__ == "__main__":
    path = "ifc_files/original_bim.ifc"
    db_config = {
        "dbname": "ifc",
        "user": "postgres",
        # "password": "your_password",  # add if needed
        "host": "localhost",
    }
    ifc_exporter = IFCExport(path, db_config)
    ifc_exporter.run()
