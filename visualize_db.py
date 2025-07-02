import psycopg2
import trimesh

# Connect to database
conn = psycopg2.connect(
    dbname="your_db", user="your_user", password="your_password", host="localhost"
)
cur = conn.cursor()

# Retrieve geometry for a specific element
cur.execute("SELECT geometry FROM elements WHERE ifc_id = %s", ("some_ifc_id",))
stl_binary = cur.fetchone()[0]

# Save to file
with open("output.stl", "wb") as f:
    f.write(stl_binary)

# Load and visualize with trimesh (requires trimesh: pip install trimesh)
mesh = trimesh.load("output.stl")
mesh.show()

cur.close()
conn.close()
