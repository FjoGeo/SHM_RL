from neo4j import GraphDatabase
from pyvis.network import Network
import json
import os
from neo4j.exceptions import ServiceUnavailable, AuthError

# Neo4j connection info (use environment variables for security)
URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
USER = os.getenv("NEO4J_USER", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "Hurensohn123#!")  # Replace with env var in production

try:
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
except (ServiceUnavailable, AuthError) as e:
    print(f"❌ Failed to connect to Neo4j: {e}")
    exit(1)

def create_sample_data(tx):
    """Create sample data in Neo4j within a transaction."""
    try:
        # 1️⃣ Delete all existing nodes
        tx.run("MATCH (n) DETACH DELETE n")

        # 2️⃣ Create new nodes and relationships
        tx.run("""
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
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        raise

def visualize_graph(output_file="complex_neo4j_graph.html"):
    """Visualize the Neo4j graph using pyvis."""
    try:
        net = Network(height="700px", width="100%", bgcolor="#222222", font_color="white")
        net.barnes_hut(gravity=-30000, central_gravity=0.3, spring_length=110, spring_strength=0.06)

        query = """
        MATCH (a)-[r]->(b)
        RETURN labels(a) AS a_labels, a.name AS source,
               type(r) AS rel,
               labels(b) AS b_labels, b.name AS target
        """

        # Collect nodes and edges to avoid duplicates
        nodes = {}
        edges = []
        with driver.session() as session:
            results = session.run(query)
            for record in results:
                src_name = record["source"]
                tgt_name = record["target"]
                src_label = record["a_labels"][0]
                tgt_label = record["b_labels"][0]
                rel = record["rel"]

                # Color and size based on node type
                color_map = {"Person": "#66ccff", "Company": "#ffcc66"}
                size_map = {"Person": 25, "Company": 40}

                # Add source node if not already added
                if src_name not in nodes:
                    nodes[src_name] = {
                        "label": src_name,
                        "color": color_map.get(src_label, "#cccccc"),
                        "shape": "dot",
                        "size": size_map.get(src_label, 25)
                    }

                # Add target node if not already added
                if tgt_name not in nodes:
                    nodes[tgt_name] = {
                        "label": tgt_name,
                        "color": color_map.get(tgt_label, "#cccccc"),
                        "shape": "dot",
                        "size": size_map.get(tgt_label, 25)
                    }

                # Add edge
                edges.append((src_name, tgt_name, rel))

        # Add nodes and edges to the network
        for node_id, node_attrs in nodes.items():
            net.add_node(node_id, **node_attrs)
        for src, tgt, rel in edges:
            net.add_edge(src, tgt, title=rel, color="#aaaaaa")

        # Configure visualization options
        options = {
            "nodes": {
                "font": {"size": 16, "color": "white"},
                "borderWidth": 2
            },
            "edges": {
                "color": {"color": "#aaaaaa", "highlight": "#ff0000"},
                "smooth": False
            },
            "physics": {
                "stabilization": True,
                "barnesHut": {
                    "gravitationalConstant": -8000,
                    "springConstant": 0.002,
                    "springLength": 150
                }
            }
        }
        net.set_options(json.dumps(options))

        # Save the visualization
        net.save_graph(output_file)
        print(f"✅ Visualization saved as {output_file} — open it in your browser.")
    except Exception as e:
        print(f"❌ Error visualizing graph: {e}")
        raise

def main():
    try:
        with driver.session() as session:
            session.execute_write(create_sample_data)
        visualize_graph()
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        driver.close()
        print("✅ Neo4j driver closed.")

if __name__ == "__main__":
    main()