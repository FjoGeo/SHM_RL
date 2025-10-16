from neo4j import GraphDatabase
import networkx as nx
import matplotlib.pyplot as plt

# Neo4j connection info
uri = "bolt://localhost:7687"
user = "neo4j"
password = "Hurensohn123#!"

driver = GraphDatabase.driver(uri, auth=(user, password))

def get_graph_data():
    query = """
    MATCH (a)-[r]->(b)
    RETURN a.name AS source, type(r) AS rel, b.name AS target
    """
    with driver.session() as session:
        result = session.run(query)
        return [(record["source"], record["target"], record["rel"]) for record in result]

def visualize_graph(data):
    G = nx.DiGraph()  # directed graph

    for src, tgt, rel in data:
        G.add_edge(src, tgt, label=rel)

    pos = nx.spring_layout(G, seed=42)  # layout algorithm
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=2000, font_size=12, font_weight='bold')
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='red')

    plt.title("Neo4j Graph Visualization")
    plt.show()

if __name__ == "__main__":
    data = get_graph_data()
    visualize_graph(data)
    driver.close()
