from neo4j import GraphDatabase
from pyvis.network import Network

# Neo4j connection info
uri = "bolt://localhost:7687"
user = "neo4j"
password = "Hurensohn123#!"  # <-- Change this

driver = GraphDatabase.driver(uri, auth=(user, password))

def create_sample_data():
    with driver.session() as session:
        # 1️⃣ Delete all existing nodes
        session.run("MATCH (n) DETACH DELETE n")

        # 2️⃣ Create new nodes and relationships
        session.run("""
        CREATE (alice:Person {name: 'Alice', age: 30}),
               (bob:Person {name: 'Bob', age: 35}),
               (carol:Person {name: 'Carol', age: 29}),
               (dave:Person {name: 'Dave', age: 40}),
               (acme:Company {name: 'Acme Corp'}),
               (globex:Company {name: 'Globex Inc.'}),
               (initech:Company {name: 'Initech'}),
               (alice)-[:KNOWS]->(bob),
               (bob)-[:KNOWS]->(carol),
               (carol)-[:KNOWS]->(alice),
               (dave)-[:KNOWS]->(bob),
               (alice)-[:WORKS_AT]->(acme),
               (bob)-[:WORKS_AT]->(globex),
               (carol)-[:WORKS_AT]->(acme),
               (dave)-[:WORKS_AT]->(initech)
        """)
    print("✅ Sample data created in Neo4j.")

def visualize_graph():
    net = Network(height="700px", width="100%", bgcolor="#222222", font_color="white")
    net.barnes_hut(gravity=-30000, central_gravity=0.3, spring_length=110, spring_strength=0.06)

    query = """
    MATCH (a)-[r]->(b)
    RETURN labels(a) AS a_labels, a.name AS source,
           type(r) AS rel,
           labels(b) AS b_labels, b.name AS target
    """

    with driver.session() as session:
        results = session.run(query)
        for record in results:
            src_label = record["a_labels"][0]
            tgt_label = record["b_labels"][0]
            rel = record["rel"]

            # Choose colors based on type
            color_map = {
                "Person": "#66ccff",  # light blue
                "Company": "#ffcc66"  # yellow-orange
            }

            # Add nodes with custom colors
            net.add_node(record["source"], 
                         label=record["source"], 
                         color=color_map.get(src_label, "#cccccc"),
                         shape="dot",
                         size=25 if src_label == "Person" else 40)

            net.add_node(record["target"], 
                         label=record["target"], 
                         color=color_map.get(tgt_label, "#cccccc"),
                         shape="dot",
                         size=25 if tgt_label == "Person" else 40)

            # Add relationship edge
            net.add_edge(record["source"], record["target"], title=rel, color="#aaaaaa")

    net.set_options("""
    const options = {
      nodes: {
        font: { size: 16, color: 'white' },
        borderWidth: 2
      },
      edges: {
        color: { color: '#aaaaaa', highlight: '#ff0000' },
        smooth: false
      },
      physics: {
        stabilization: true,
        barnesHut: {
          gravitationalConstant: -8000,
          springConstant: 0.002,
          springLength: 150
        }
      }
    }
    """)
    
    net.save_graph("complex_neo4j_graph.html")
    print("✅ Visualization saved as complex_neo4j_graph.html — open it in your browser.")

if __name__ == "__main__":
    create_sample_data()
    visualize_graph()
    driver.close()
