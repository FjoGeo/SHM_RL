##Copyright 2016 Thomas Paviot (tpaviot@gmail.com)
##
##This file is part of pythonOCC.
##
##pythonOCC is free software: you can redistribute it and/or modify
##it under the terms of the GNU Lesser General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##
##pythonOCC is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU Lesser General Public License for more details.
##
##You should have received a copy of the GNU Lesser General Public License
##along with pythonOCC.  If not, see <http://www.gnu.org/licenses/>.


from __future__ import print_function

try:
    import ifcopenshell
    import ifcopenshell.geom.occ_utils
    from ifcopenshell import geom
except ImportError:
    print(
        "This example requires ifcopenshell for python. Please go to  http://ifcopenshell.org/python.html"
    )
import ifc_metadata
from OCC.Display.SimpleGui import init_display

# viewer settings
settings = geom.settings()
settings.set(settings.USE_PYTHON_OPENCASCADE, True)


# Override the close event
def on_close():
    display.Close()  # Close the display context


def visualize_ifc(product_shapes):
    # Initialize a graphical display window
    global display
    print("Initializing pythonocc display ...", end="")
    display, start_display, add_menu, add_function_to_menu = init_display()
    print("initialization ok.")

    # print(dir(display))
    # print(dir(display.Context))
    # Adjust tessellation quality
    # Set the deflection for tessellation
    display.Context.SetDeviationAngle(0.02)  # Lower value = smoother curves
    display.Context.SetDeviationCoefficient(0.0005)  # Controls linear deflection

    # then pass each shape to the display
    nbr_shapes = len(product_shapes)
    idx = 0
    for ps in product_shapes:
        display.DisplayShape((ps[1]))
        idx += 1
        # progress bar
        print(
            "[%i%%] Sending shapes to pythonocc display." % int(idx * 100 / nbr_shapes)
        )
    display.FitAll()
    display.display_graduated_trihedron()
    start_display()


if __name__ == "__main__":
    # Open the IFC file using IfcOpenShell
    filepath = "./sample_data/ifc_file/20005_ARC_GMOD_GEOREF_IA_210408.ifc"
    print("Opening IFC file %s ..." % filepath, end="")
    ifc_file = ifcopenshell.open(filepath)
    print("file opened.")
    # The geometric elements in an IFC file are the IfcProduct elements.
    # So these are opened and displayed.
    products = ifc_file.by_type("IfcProduct")
    metadata = ifc_metadata.metadata_dictionary(ifc_file)

    # First filter products to display
    # just keep the ones with a 3d representation
    products_to_display = []
    for product in products:
        if (
            product.is_a("IfcOpeningElement")
            or product.is_a("IfcSite")
            or product.is_a("IfcAnnotation")
        ):
            continue
        if product.Representation is not None:
            products_to_display.append(product)
    print("Products to display: %i" % len(products_to_display))
    # For every product a shape is created if the shape has a Representation.
    print("Traverse data with associated 3d geometry")
    idx = 0
    product_shapes = []
    for product in products_to_display:
        try:
            # display current product
            shape = ifcopenshell.geom.create_shape(settings, product).geometry
            product_shapes.append((product, shape))
            idx += 1
            print(
                "\r[%i%%]Product: %s"
                % (int(idx * 100 / len(products_to_display)), product)
            )
            metadata1 = metadata[product]
        except:
            print("Error while processing product: %s" % product)

    visualize_ifc(product_shapes)
