import ifcopenshell
import ifcopenshell.util.element

# Load your IFC file
source_ifc = ifcopenshell.open("./original_bim.ifc")


# Create a new empty IFC file (same schema)
new_ifc = ifcopenshell.file(schema=source_ifc.schema)

# Copy the basic project structure from the original
project = source_ifc.by_type("IfcProject")[0]
site = source_ifc.by_type("IfcSite")[0]
building = source_ifc.by_type("IfcBuilding")[0]
building_storey = source_ifc.by_type("IfcBuildingStorey")[0]

# Add them to the new file
new_project = new_ifc.add(project)
new_site = new_ifc.add(site)
new_building = new_ifc.add(building)
new_storey = new_ifc.add(building_storey)

# Create a containment structure
rel_aggregate = new_ifc.create_entity(
    "IfcRelAggregates",
    GlobalId=ifcopenshell.guid.new(),
    RelatingObject=new_project,
    RelatedObjects=[new_site],
)
new_ifc.add(rel_aggregate)

rel_aggregate_site = new_ifc.create_entity(
    "IfcRelAggregates",
    GlobalId=ifcopenshell.guid.new(),
    RelatingObject=new_site,
    RelatedObjects=[new_building],
)
new_ifc.add(rel_aggregate_site)

rel_aggregate_building = new_ifc.create_entity(
    "IfcRelAggregates",
    GlobalId=ifcopenshell.guid.new(),
    RelatingObject=new_building,
    RelatedObjects=[new_storey],
)
new_ifc.add(rel_aggregate_building)


walls = (
    source_ifc.by_type("IfcWall")
    + source_ifc.by_type("IfcWallStandardCase")
    + source_ifc.by_type("IfcCurtainWall")
    + source_ifc.by_type("IfcBuildingElementPart")
)


for wall in walls:
    is_external = False
    for rel in wall.IsDefinedBy:
        if rel.is_a("IfcRelDefinesByProperties"):
            prop_set = rel.RelatingPropertyDefinition
            if prop_set.is_a("IfcPropertySet"):
                for prop in prop_set.HasProperties:
                    if prop.Name == "IsExternal":
                        is_external = prop.NominalValue.wrappedValue
    if is_external:
        new_wall = new_ifc.add(wall)
        rel_contained = new_ifc.create_entity(
            "IfcRelContainedInSpatialStructure",
            GlobalId=ifcopenshell.guid.new(),
            RelatingStructure=new_storey,
            RelatedElements=[new_wall],
        )
        new_ifc.add(rel_contained)

        # print(f"Outer Wall: {wall.GlobalId}, Name: {wall.Name}")

new_ifc.write("outer_walls.ifc")
print("Exported!")
