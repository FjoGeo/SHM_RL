from neo4j import GraphDatabase
from pyvis.network import Network

uri = "bolt://localhost:7687"
user = "neo4j"
password = "Hurensohn123#!"

driver = GraphDatabase.driver(uri, auth=(user, password))

def visualize_interactive():
    net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
    query = "MATCH (a)-[r]->(b) RETURN a.name AS source, type(r) AS rel, b.name AS target"

    with driver.session() as session:
        for record in session.run(query):
            net.add_node(record["source"], label=record["source"])
            net.add_node(record["target"], label=record["target"])
            net.add_edge(record["source"], record["target"], title=record["rel"])

    # Save the interactive graph as an HTML file
    net.save_graph("neo4j_graph.html")
    print("✅ Graph saved to neo4j_graph.html — open it in your browser to view.")

if __name__ == "__main__":
    visualize_interactive()
    driver.close()