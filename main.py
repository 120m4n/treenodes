"""
Main script for building electrical network hierarchy and storing in SQLite.

This script:
1. Loads nodes and segments from CSV files
2. Builds a network graph using NetworkX (with abstraction for future flexibility)
3. Performs BFS traversal to build a closure table
4. Stores all data in a SQLite database
"""

import sys
from pathlib import Path
from data_loader import DataLoader
from network_builder import NetworkBuilder
from database import NetworkDatabase


def main():
    """Main execution function."""
    print("=" * 60)
    print("Electrical Network Hierarchy Builder")
    print("=" * 60)
    
    # Configuration
    data_dir = Path(__file__).parent / 'data'
    db_path = 'network.db'
    use_networkx = True  # Set to False to use manual implementation
    
    print(f"\n1. Loading data from: {data_dir}")
    # Load data from CSV files
    loader = DataLoader(data_dir)
    try:
        nodos, segmentos = loader.load_all()
        print(f"   ✓ Loaded {len(nodos)} nodes")
        print(f"   ✓ Loaded {len(segmentos)} segments")
    except Exception as e:
        print(f"   ✗ Error loading data: {e}")
        sys.exit(1)
    
    print(f"\n2. Building network (using {'NetworkX' if use_networkx else 'manual implementation'})")
    # Build the network
    builder = NetworkBuilder(use_networkx=use_networkx)
    try:
        builder.build_network(nodos, segmentos)
        network = builder.get_network()
        print(f"   ✓ Network built with {len(network.get_nodes())} nodes")
    except Exception as e:
        print(f"   ✗ Error building network: {e}")
        sys.exit(1)
    
    print("\n3. Performing BFS traversal to build closure table")
    # Perform BFS traversal from all connected components
    all_closure_entries = []
    visited_global = set()
    
    try:
        for start_node in network.get_nodes():
            if start_node not in visited_global:
                # Perform BFS from this starting node
                closure_entries = network.bfs_traversal(start_node)
                all_closure_entries.extend(closure_entries)
                
                # Mark all nodes in this component as visited
                for ancestor, descendant, depth in closure_entries:
                    visited_global.add(ancestor)
                    visited_global.add(descendant)
        
        print(f"   ✓ Generated {len(all_closure_entries)} closure table entries")
    except Exception as e:
        print(f"   ✗ Error during BFS traversal: {e}")
        sys.exit(1)
    
    print(f"\n4. Storing data in SQLite database: {db_path}")
    # Store everything in SQLite database
    try:
        with NetworkDatabase(db_path) as db:
            print("   - Creating tables...")
            db.create_tables()
            
            print("   - Inserting nodes...")
            db.insert_nodos(nodos)
            
            print("   - Inserting segments...")
            db.insert_segmentos(segmentos)
            
            print("   - Inserting closure table...")
            db.insert_closure_table(all_closure_entries)
            
            # Get and display statistics
            stats = db.get_statistics()
            print(f"\n   ✓ Database created successfully!")
            print(f"     - Nodes: {stats['nodos']}")
            print(f"     - Segments: {stats['segmentos']}")
            print(f"     - Closure entries: {stats['closure_entries']}")
    except Exception as e:
        print(f"   ✗ Error storing data in database: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("Process completed successfully!")
    print("=" * 60)
    print(f"\nDatabase file created: {db_path}")
    print("\nYou can query the database using SQLite:")
    print(f"  sqlite3 {db_path}")
    print("\nAvailable tables:")
    print("  - nodos_circuito: Network nodes")
    print("  - segmentos_circuito: Network segments")
    print("  - closure_table: Hierarchical relationships")
    print()


if __name__ == "__main__":
    main()
