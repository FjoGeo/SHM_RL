import ifcopenshell
import ifcopenshell.geom


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

    def get_metadata(self, ifc_file):
        """Extract the metadata from the filtered ifc file"""

        # I need
        # {'ArchiCADProperties':  {
        # 'Ursprungsgeschoss Name': '0EG',
        # 'Ursprungsgeschoss Nummer': '0' }}
        # geometry, ID, coordinates
        pass

    def run(self):
        ifc_file = self.load_ifc_file()
        ifc_file = self.select_POI(ifc_file)
        self.get_metadata(ifc_file)


if __name__ == "__main__":
    path = "./original_bim.ifc"
    ifc_exporter = IFCExport(path)
    ifc_exporter.run()
