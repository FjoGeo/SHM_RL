import ifc_processing.ifc_metadata as ifcm
import ifcopenshell
import tqdm
from visualization.visualize_ifc import visualize_ifc


class IFCParser:
    def __init__(self, file_path):
        self.ifc_name = file_path
        self.ifc = None
        self.ifc_metadata = None
        self.products = None
        self.product_shape_per_floor = {}
        self.num2name_mapping = {}

        # viewer settings
        self.settings = ifcopenshell.geom.settings()
        self.settings.set(self.settings.USE_PYTHON_OPENCASCADE, True)

    def parse_ifc(self):
        """
        Parses the IFC file specified during initialization.

        This method opens the IFC file, extracts metadata, and retrieves all
        products of type `IfcProduct` from the file. The parsed data is stored
        in the `self.ifc`, `self.ifc_metadata`, and `self.products` attributes.

        Raises:
            Exception: If the IFC file cannot be opened or parsed.
        """
        print("Opening IFC file %s ..." % self.ifc_name, end="")
        self.ifc = ifcopenshell.open(self.ifc_name)
        print("file opened.")
        self.ifc_metadata = ifcm.metadata_dictionary(self.ifc)
        self.products = self.ifc.by_type("IfcProduct")

    def convert_to_svg_by_floor_number(self, floor_number, pixels_per_m=20):
        """
        Converts the specified floor of the IFC model to an SVG representation.

        Args:
            floor_number (int): The floor number to convert to SVG.
            pixels_per_m (int, optional): The scale of the SVG in pixels per meter. Defaults to 20.

        Returns:
            None
        """
        floor_name = self.get_floor_name(floor_number)
        self.convert_to_svg_by_floor_name(floor_name, pixels_per_m)

    def separate_by_floor(self):
        """
        Segregates IFC elements by their associated floor.

        This method iterates through all `IfcProduct` elements in the IFC file and groups them
        based on their floor information. The floor name and number are extracted from the
        `ArchiCADProperties` metadata. Elements that do not belong to a specific floor or are
        of certain types (e.g., `IfcOpeningElement`, `IfcSite`, `IfcAnnotation`) are skipped.

        The grouped elements are stored in the `self.product_shape_per_floor` dictionary,
        where the keys are floor names and the values are lists of tuples containing the
        product and its geometry.

        Raises:
            Exception: If there is an error while processing a product.
        """
        floors_name = set()

        for product in tqdm.tqdm(
            self.products, desc="Segregating elements based on floor: "
        ):
            if (
                product.is_a("IfcOpeningElement")
                or product.is_a("IfcSite")
                or product.is_a("IfcAnnotation")
            ):
                continue
            elif product.is_a("IfcBuildingElementPart"):
                floor_name = self.get_storey_of_part(product)
                if floor_name not in floors_name:
                    floors_name.add(floor_name)
                    self.product_shape_per_floor[floor_name] = []
                shape = ifcopenshell.geom.create_shape(self.settings, product).geometry
                self.product_shape_per_floor[floor_name].append((product, shape))
            else:
                metadata1 = self.ifc_metadata[product]
                # print(metadata1)

                try:
                    if "ArchiCADProperties" not in metadata1.keys():
                        continue
                    # if the floor name not in floors_name, add it to the set
                    if (
                        metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                        not in floors_name
                    ):
                        floors_name.add(
                            metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                        )
                        # initialize it as well
                        self.product_shape_per_floor[
                            metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                        ] = []
                    if (
                        metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                        not in self.num2name_mapping.keys()
                    ):
                        self.num2name_mapping[
                            metadata1["ArchiCADProperties"]["Ursprungsgeschoss Nummer"]
                        ] = metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                    # now add elements
                    shape = ifcopenshell.geom.create_shape(
                        self.settings, product
                    ).geometry
                    self.product_shape_per_floor[
                        metadata1["ArchiCADProperties"]["Ursprungsgeschoss Name"]
                    ].append((product, shape))
                    # print(self.product_shape_per_floor)
                except Exception as e:
                    pass
                    # print("Error while processing product: %s" % product)
                    # print("Exception: %s" % str(e))
                finally:
                    pass

    def visualize_ifc_by_floor_name(self, floor_name):
        visualize_ifc(self.product_shape_per_floor[floor_name])

    def get_floor_name(self, floor_n):
        return self.num2name_mapping[str(floor_n)]

    def visualize_ifc_by_floor_number(self, floor_num):
        floor_name = self.get_floor_name(floor_num)
        self.visualize_ifc_by_floor_name(floor_name)

    @staticmethod
    def get_storey_of_element(elem):
        """Return the IfcBuildingStorey the element is contained in, or None."""
        for rel in getattr(elem, "ContainedInStructure", []):
            if rel.is_a("IfcRelContainedInSpatialStructure"):
                storey = rel.RelatingStructure
                if storey.is_a("IfcBuildingStorey"):
                    return storey
        return None

    @staticmethod
    def get_host_element(elem):
        """Return the element this part is decomposed from (e.g., IfcWall)."""
        for rel in getattr(elem, "Decomposes", []):
            if rel.is_a("IfcRelAggregates"):
                return rel.RelatingObject
        return None

    def get_storey_of_part(self, part):
        """Return the name of the storey associated with a part, or its host's storey."""
        storey = self.get_storey_of_element(part)
        if storey:
            return storey.Name
        host = self.get_host_element(part)
        if host:
            storey = self.get_storey_of_element(host)
            if storey:
                return storey.Name
        return None


if __name__ == "__main__":
    filepath = "./sample_data/ifc_file/20005_ARC_GMOD_GEOREF_IA_210408.ifc"
    ifc_parser = IFCParser(filepath)
    ifc_parser.parse_ifc()
    ifc_parser.separate_by_floor()
    ifc_parser.visualize_ifc_by_floor_number(4)
