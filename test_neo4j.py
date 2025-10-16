from neo4j import GraphDatabase

# Connection details
uri = "bolt://localhost:7687"   # or the Aura URL like "neo4j+s://<your-id>.databases.neo4j.io"
user = "neo4j"
password = "Hurensohn123#!"

# Create driver
driver = GraphDatabase.driver(uri, auth=(user, password))

def test_neo4j():
    with driver.session() as session:
        # Create some data
        session.run("CREATE (a:Person {name: 'Alice'})")
        session.run("CREATE (b:Person {name: 'Bob'})")
        session.run("MATCH (a:Person {name:'Alice'}), (b:Person {name:'Bob'}) "
                    "CREATE (a)-[:KNOWS]->(b)")
        
        # Query the data
        result = session.run("MATCH (a)-[:KNOWS]->(b) RETURN a.name, b.name")
        
        for record in result:
            print(f"{record['a.name']} knows {record['b.name']}")

if __name__ == "__main__":
    test_neo4j()
    driver.close()