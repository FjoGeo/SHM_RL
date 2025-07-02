import ifcopenshell
import ifcopenshell.geom
from ifcopenshell.util import placement


class IFCExport:
    def __init__(self, path):
        self.path = path
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_PYTHON_OPENCASCADE, True)

    def load_ifc_file(self):
        """Load IFC file / BIM model."""
        return ifcopenshell.open(self.path)

    def select_POI(self, ifc_file):
        """Select walls and similar elements."""
        return (
            ifc_file.by_type("IfcWall")
            + ifc_file.by_type("IfcWallStandardCase")
            + ifc_file.by_type("IfcCurtainWall")
            + ifc_file.by_type("IfcBuildingElementPart")
        )

    def get_metadata(self, elements):
        """Extract and print metadata from the selected IFC elements."""
        for element in elements:
            print("Element ID:", element.GlobalId)
            try:
                matrix = placement.get_local_placement(element.ObjectPlacement)
                coordinates = matrix[:3, 3]
                print("Absolute Coordinates:", tuple(coordinates))
            except Exception:
                print("Unable to get coordinates")
            if element.Representation:
                rep_types = [
                    rep.RepresentationType
                    for rep in element.Representation.Representations
                ]
                print("Geometry Representations:", rep_types)
            else:
                print("No geometry representation")
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
                                if prop.Name == "Ursprungsgeschoss Name":
                                    print(
                                        "Ursprungsgeschoss Name:",
                                        prop.NominalValue.wrappedValue,
                                    )
                                elif prop.Name == "Ursprungsgeschoss Nummer":
                                    print(
                                        "Ursprungsgeschoss Nummer:",
                                        prop.NominalValue.wrappedValue,
                                    )
            print("---")

    def run(self):
        ifc_file = self.load_ifc_file()
        elements = self.select_POI(ifc_file)
        self.get_metadata(elements)


if __name__ == "__main__":
    path = "./original_bim.ifc"
    ifc_exporter = IFCExport(path)
    ifc_exporter.run()
