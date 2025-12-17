# TreeNodes - Electrical Network Hierarchy Builder

This project implements a Python-based system to model and analyze electrical network hierarchies using graph theory and closure tables.

## Overview

The system reads electrical network data from CSV files, builds a graph representation, performs hierarchical analysis using BFS (Breadth-First Search), and stores the results in a SQLite database.

## Features

- **CSV Data Import**: Load nodes and segments from CSV files
- **Graph Construction**: Build network using NetworkX library
- **Abstraction Layer**: Architecture designed to support manual graph implementation (future-proof, not dependent on NetworkX)
- **BFS Traversal**: Traverse the network using BFS algorithm with stack/queue
- **Closure Table**: Generate hierarchical relationships for efficient querying
- **SQLite Storage**: Store all data in a single SQLite database

## Installation

1. Clone the repository:
```bash
git clone https://github.com/120m4n/treenodes.git
cd treenodes
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the main script to process the network data:

```bash
python main.py
```

This will:
1. Load nodes from `data/nodos_circuito.csv`
2. Load segments from `data/segmentos_circuito.csv`
3. Build the network graph
4. Perform BFS traversal to create closure table
5. Store everything in `network.db`

## Data Structure

### Input CSV Files

#### nodos_circuito.csv
Contains network nodes with the following fields:
- `id_nodo`: Unique node identifier (INTEGER)
- `nombre`: Node name/label (TEXT)
- `tipo`: Node type (e.g., "POSTE EN H", "POSTE SENCILLO", "AEREO") (TEXT)
- `voltaje_kv`: Voltage in kilovolts (REAL)
- `x`: X coordinate (REAL)
- `y`: Y coordinate (REAL)

#### segmentos_circuito.csv
Contains network segments (edges) with the following fields:
- `id_segmento`: Unique segment identifier (INTEGER)
- `id_circuito`: Circuit identifier (TEXT)
- `nodo_inicio`: Starting node ID (INTEGER)
- `nodo_fin`: Ending node ID (INTEGER)
- `longitud_m`: Length in meters (REAL)
- `tipo_conductor`: Conductor type code (INTEGER)
- `capacidad_amp`: Capacity in amperes (INTEGER)

### Database Schema

The SQLite database (`network.db`) contains three tables:

#### nodos_circuito
Stores all network nodes with the same structure as the CSV file.

#### segmentos_circuito
Stores all network segments with the same structure as the CSV file.

#### closure_table
Stores hierarchical relationships discovered through BFS traversal:
- `ancestor`: Ancestor node ID (INTEGER)
- `descendant`: Descendant node ID (INTEGER)
- `depth`: Distance between ancestor and descendant (INTEGER)

The closure table allows efficient hierarchical queries such as:
- Find all descendants of a node
- Find all ancestors of a node
- Find nodes at a specific depth
- Calculate path lengths

## Architecture

### Design Principles

The system is built with modularity and future extensibility in mind:

1. **Abstraction Layer**: `NetworkInterface` defines common operations independent of implementation
2. **Multiple Implementations**: 
   - `NetworkXAdapter`: Uses NetworkX library (current default)
   - `ManualNetworkAdapter`: Pure Python implementation using adjacency lists
3. **Easy Switching**: Change `use_networkx` parameter in `main.py` to switch implementations

### Module Structure

```
treenodes/
├── data/
│   ├── nodos_circuito.csv      # Node data
│   └── segmentos_circuito.csv  # Segment data
├── models.py                    # Data models (Nodo, Segmento)
├── data_loader.py              # CSV loading functionality
├── network_builder.py          # Network construction and BFS traversal
├── database.py                 # SQLite database operations
├── main.py                     # Main execution script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

### Class Diagram

```
NetworkInterface (Abstract)
├── NetworkXAdapter
└── ManualNetworkAdapter

DataLoader
├── load_nodos()
└── load_segmentos()

NetworkBuilder
├── build_network()
└── bfs_traversal()

NetworkDatabase
├── create_tables()
├── insert_nodos()
├── insert_segmentos()
└── insert_closure_table()
```

## Example Queries

Once the database is created, you can query it using SQLite:

```bash
sqlite3 network.db
```

### Find all nodes
```sql
SELECT * FROM nodos_circuito LIMIT 10;
```

### Find all segments connected to a specific node
```sql
SELECT * FROM segmentos_circuito 
WHERE nodo_inicio = 655795 OR nodo_fin = 655795;
```

### Find all descendants of a node
```sql
SELECT n.* 
FROM closure_table ct
JOIN nodos_circuito n ON ct.descendant = n.id_nodo
WHERE ct.ancestor = 3 AND ct.depth >= 0;
```

### Find all ancestors of a node
```sql
SELECT ct.ancestor, n.tipo, n.nombre
FROM closure_table ct
JOIN nodos_circuito n ON ct.ancestor = n.id_nodo
WHERE ct.descendant = 10 AND ct.depth!=0 order by ct.depth desc;
```

### Find nodes at specific depth from a node
```sql
SELECT n.* 
FROM closure_table ct
JOIN nodos_circuito n ON ct.descendant = n.id_nodo
WHERE ct.ancestor = 1 AND ct.depth = 2;
```

## Future Enhancements

The architecture supports the following future improvements:

1. **Custom Graph Algorithms**: Implement specialized algorithms without NetworkX dependency
2. **Directed Graphs**: Modify to support directed electrical flow
3. **Weighted Paths**: Incorporate segment properties (length, capacity) in path calculations
4. **Real-time Updates**: Add/remove nodes and segments dynamically
5. **Visualization**: Add network visualization capabilities
6. **Performance Optimization**: Optimize for very large networks

## Field Mapping Reference

All database table names and column names are derived directly from the CSV file headers:

| CSV File | Table Name | Purpose |
|----------|------------|---------|
| `nodos_circuito.csv` | `nodos_circuito` | Network nodes |
| `segmentos_circuito.csv` | `segmentos_circuito` | Network segments |
| (Generated) | `closure_table` | Hierarchical relationships |

## Literature

https://web.archive.org/web/20130701143352/http://technobytz.com/closure_table_store_hierarchical_data.html

## License

This project is part of the 120m4n/treenodes repository.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
