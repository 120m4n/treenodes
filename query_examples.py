"""
Example queries demonstrating the use of the closure table for hierarchical queries.
"""

import sqlite3
from pathlib import Path


def connect_db(db_path: str = 'network.db'):
    """Connect to the SQLite database."""
    return sqlite3.connect(db_path)


def print_separator(title: str = ""):
    """Print a formatted separator."""
    print("\n" + "=" * 70)
    if title:
        print(f" {title}")
        print("=" * 70)


def query_1_all_descendants(conn, node_id: int):
    """Find all descendants of a given node."""
    print_separator(f"Query 1: All descendants of node {node_id}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ct.descendant,
            n.nombre,
            n.tipo,
            ct.depth
        FROM closure_table ct
        JOIN nodos_circuito n ON ct.descendant = n.id_nodo
        WHERE ct.ancestor = ? AND ct.depth > 0
        ORDER BY ct.depth, ct.descendant
        LIMIT 20
    """, (node_id,))
    
    results = cursor.fetchall()
    if results:
        print(f"\nFound {len(results)} descendants (showing first 20):\n")
        print(f"{'Node ID':<12} {'Name':<12} {'Type':<25} {'Depth':<6}")
        print("-" * 70)
        for row in results:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<25} {row[3]:<6}")
    else:
        print(f"\nNo descendants found for node {node_id}")


def query_2_all_ancestors(conn, node_id: int):
    """Find all ancestors of a given node."""
    print_separator(f"Query 2: All ancestors of node {node_id}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ct.ancestor,
            n.nombre,
            n.tipo,
            ct.depth
        FROM closure_table ct
        JOIN nodos_circuito n ON ct.ancestor = n.id_nodo
        WHERE ct.descendant = ? AND ct.depth > 0
        ORDER BY ct.depth DESC
        LIMIT 20
    """, (node_id,))
    
    results = cursor.fetchall()
    if results:
        print(f"\nFound {len(results)} ancestors (showing first 20):\n")
        print(f"{'Node ID':<12} {'Name':<12} {'Type':<25} {'Depth':<6}")
        print("-" * 70)
        for row in results:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<25} {row[3]:<6}")
    else:
        print(f"\nNo ancestors found for node {node_id}")


def query_3_nodes_at_depth(conn, node_id: int, depth: int):
    """Find all nodes at a specific depth from a given node."""
    print_separator(f"Query 3: Nodes at depth {depth} from node {node_id}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            ct.descendant,
            n.nombre,
            n.tipo
        FROM closure_table ct
        JOIN nodos_circuito n ON ct.descendant = n.id_nodo
        WHERE ct.ancestor = ? AND ct.depth = ?
        ORDER BY ct.descendant
        LIMIT 10
    """, (node_id, depth))
    
    results = cursor.fetchall()
    if results:
        print(f"\nFound {len(results)} nodes at depth {depth} (showing first 10):\n")
        print(f"{'Node ID':<12} {'Name':<12} {'Type':<25}")
        print("-" * 70)
        for row in results:
            print(f"{row[0]:<12} {row[1]:<12} {row[2]:<25}")
    else:
        print(f"\nNo nodes found at depth {depth} from node {node_id}")


def query_4_network_statistics(conn):
    """Display general network statistics."""
    print_separator("Query 4: Network Statistics")
    
    cursor = conn.cursor()
    
    # Total counts
    cursor.execute("SELECT COUNT(*) FROM nodos_circuito")
    total_nodes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM segmentos_circuito")
    total_segments = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM closure_table")
    total_closure = cursor.fetchone()[0]
    
    # Node types
    cursor.execute("""
        SELECT tipo, COUNT(*) as count
        FROM nodos_circuito
        GROUP BY tipo
        ORDER BY count DESC
        LIMIT 5
    """)
    node_types = cursor.fetchall()
    
    # Max depth
    cursor.execute("SELECT MAX(depth) FROM closure_table")
    max_depth = cursor.fetchone()[0]
    
    print(f"\nTotal Nodes: {total_nodes}")
    print(f"Total Segments: {total_segments}")
    print(f"Total Closure Entries: {total_closure}")
    print(f"Maximum Tree Depth: {max_depth}")
    
    print(f"\nTop 5 Node Types:")
    print(f"{'Type':<30} {'Count':<10}")
    print("-" * 70)
    for tipo, count in node_types:
        print(f"{tipo:<30} {count:<10}")


def query_5_segment_details(conn, node_id: int):
    """Find all segments connected to a specific node."""
    print_separator(f"Query 5: Segments connected to node {node_id}")
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            s.id_segmento,
            s.nodo_inicio,
            s.nodo_fin,
            s.longitud_m,
            s.capacidad_amp,
            CASE 
                WHEN s.nodo_inicio = ? THEN 'Outgoing'
                ELSE 'Incoming'
            END as direction
        FROM segmentos_circuito s
        WHERE s.nodo_inicio = ? OR s.nodo_fin = ?
        ORDER BY s.id_segmento
        LIMIT 10
    """, (node_id, node_id, node_id))
    
    results = cursor.fetchall()
    if results:
        print(f"\nFound {len(results)} connected segments (showing first 10):\n")
        print(f"{'Segment ID':<12} {'From':<10} {'To':<10} {'Length(m)':<12} {'Capacity':<10} {'Direction':<10}")
        print("-" * 70)
        for row in results:
            print(f"{row[0]:<12} {row[1]:<10} {row[2]:<10} {row[3]:<12.2f} {row[4]:<10} {row[5]:<10}")
    else:
        print(f"\nNo segments found connected to node {node_id}")


def main():
    """Run example queries."""
    db_path = Path(__file__).parent / 'network.db'
    
    if not db_path.exists():
        print(f"Error: Database file '{db_path}' not found.")
        print("Please run 'python main.py' first to create the database.")
        return
    
    print("\n" + "=" * 70)
    print(" ELECTRICAL NETWORK DATABASE - QUERY EXAMPLES")
    print("=" * 70)
    
    conn = connect_db(str(db_path))
    
    try:
        # Run various example queries
        query_4_network_statistics(conn)
        
        # Use a sample node ID that exists in the data
        sample_node = 655795
        
        query_1_all_descendants(conn, sample_node)
        query_2_all_ancestors(conn, sample_node)
        query_3_nodes_at_depth(conn, sample_node, 2)
        query_5_segment_details(conn, sample_node)
        
        print("\n" + "=" * 70)
        print(" QUERIES COMPLETED SUCCESSFULLY")
        print("=" * 70 + "\n")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()
