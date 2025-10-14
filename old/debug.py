import ifcopenshell
import ifcopenshell.geom

# Load IFC file
ifc_file = ifcopenshell.open("ifc_files/original_bim.ifc")
elements = ifc_file.by_type("IfcWall")  # Adjust as needed

# Define geometry settings
settings = ifcopenshell.geom.settings()
settings.set(settings.USE_WORLD_COORDS, True)  # Keep world coordinates for consistency
settings.set(
    settings.USE_PYTHON_OPENCASCADE, True
)  # Enable OpenCascade for robust geometry handling

# Example processing loop (adjust to match your script)
for element in ifc_file.by_type("IfcWall"):  # Or your specific element types
    print(f"Processing element {element.GlobalId}")
    for rep in element.Representation.Representations:
        if rep.RepresentationIdentifier == "Body":
            print(f"'Body' type: {rep.RepresentationType}")
            try:
                shape = ifcopenshell.geom.create_shape(settings, rep)
                if shape and hasattr(shape, "geometry") and shape.geometry.verts:
                    print(f"Geometry extracted: {len(shape.geometry.verts)} vertices")
                    # Proceed with your database storage logic here
                else:
                    print(f"Invalid shape for {element.GlobalId}, skipping.")
            except Exception as e:
                print(f"Error processing {element.GlobalId}: {e}")
# ----------


# for element in elements:
#     # Check representations
#     if element.Representation and element.Representation.Representations:
#         rep_ids = [
#             rep.RepresentationIdentifier
#             for rep in element.Representation.Representations
#         ]
#         print(f"Element {element.GlobalId} has representations: {rep_ids}")
#         body_rep = next(
#             (
#                 rep
#                 for rep in element.Representation.Representations
#                 if rep.RepresentationIdentifier == "Body"
#             ),
#             None,
#         )
#         if body_rep:
#             print(f"'Body' type: {body_rep.RepresentationType}")
#         else:
#             print(f"No 'Body' representation for {element.GlobalId}, skipping.")
#             continue
#     else:
#         print(f"No representations for {element.GlobalId}, skipping.")
#         continue
#
#     # Try to create shape
#     try:
#         shape = ifcopenshell.geom.create_shape(settings, body_rep)
#         if shape and hasattr(shape, "geometry") and shape.geometry.verts:
#             print(
#                 f"Success: {element.GlobalId} has {len(shape.geometry.verts)} vertices."
#             )
#             # Proceed with your database storage here
#         else:
#             print(f"Invalid shape for {element.GlobalId}, skipping.")
#     except Exception as e:
#         print(f"Error for {element.GlobalId}: {e}")
