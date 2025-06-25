import ifcopenshell
import ifcopenshell.util.selector

# model
model = ifcopenshell.open("./original_bim.ifc")

walls = model.by_type("IfcWall")

for wall in walls[0:10]:
    print(wall.get_info(True))
