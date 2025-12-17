"""
SQLite database handler for storing network data and closure table.
Table names and columns based on CSV headers.
"""

import sqlite3
from typing import List
from pathlib import Path
from models import Nodo, Segmento


class NetworkDatabase:
    """Manages SQLite database for electrical network data."""
    
    def __init__(self, db_path: str = 'network.db'):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Establish database connection."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def create_tables(self):
        """
        Create database tables based on CSV headers.
        
        Tables:
        - nodos_circuito: Network nodes
        - segmentos_circuito: Network segments
        - closure_table: Hierarchical relationships
        """
        cursor = self.conn.cursor()
        
        # Create nodos_circuito table (based on CSV headers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS nodos_circuito (
                id_nodo INTEGER PRIMARY KEY,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                voltaje_kv REAL NOT NULL,
                x REAL NOT NULL,
                y REAL NOT NULL
            )
        """)
        
        # Create segmentos_circuito table (based on CSV headers)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS segmentos_circuito (
                id_segmento INTEGER PRIMARY KEY,
                id_circuito TEXT NOT NULL,
                nodo_inicio INTEGER NOT NULL,
                nodo_fin INTEGER NOT NULL,
                longitud_m REAL NOT NULL,
                tipo_conductor INTEGER NOT NULL,
                capacidad_amp INTEGER NOT NULL,
                FOREIGN KEY (nodo_inicio) REFERENCES nodos_circuito(id_nodo),
                FOREIGN KEY (nodo_fin) REFERENCES nodos_circuito(id_nodo)
            )
        """)
        
        # Create closure_table for hierarchical relationships
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS closure_table (
                ancestor INTEGER NOT NULL,
                descendant INTEGER NOT NULL,
                depth INTEGER NOT NULL,
                PRIMARY KEY (ancestor, descendant),
                FOREIGN KEY (ancestor) REFERENCES nodos_circuito(id_nodo),
                FOREIGN KEY (descendant) REFERENCES nodos_circuito(id_nodo)
            )
        """)
        
        # Create indexes for better query performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_closure_ancestor 
            ON closure_table(ancestor)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_closure_descendant 
            ON closure_table(descendant)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_segmentos_nodo_inicio 
            ON segmentos_circuito(nodo_inicio)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_segmentos_nodo_fin 
            ON segmentos_circuito(nodo_fin)
        """)
        
        self.conn.commit()
    
    def insert_nodos(self, nodos: List[Nodo]):
        """
        Insert nodes into the database.
        
        Args:
            nodos: List of Nodo objects to insert
        """
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM nodos_circuito")
        
        # Insert nodes
        for nodo in nodos:
            cursor.execute("""
                INSERT INTO nodos_circuito 
                (id_nodo, nombre, tipo, voltaje_kv, x, y)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nodo.id_nodo,
                nodo.nombre,
                nodo.tipo,
                nodo.voltaje_kv,
                nodo.x,
                nodo.y
            ))
        
        self.conn.commit()
    
    def insert_segmentos(self, segmentos: List[Segmento]):
        """
        Insert segments into the database.
        
        Args:
            segmentos: List of Segmento objects to insert
        """
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM segmentos_circuito")
        
        # Insert segments
        for segmento in segmentos:
            cursor.execute("""
                INSERT INTO segmentos_circuito 
                (id_segmento, id_circuito, nodo_inicio, nodo_fin, 
                 longitud_m, tipo_conductor, capacidad_amp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                segmento.id_segmento,
                segmento.id_circuito,
                segmento.nodo_inicio,
                segmento.nodo_fin,
                segmento.longitud_m,
                segmento.tipo_conductor,
                segmento.capacidad_amp
            ))
        
        self.conn.commit()
    
    def insert_closure_table(self, closure_entries: List[tuple[int, int, int]]):
        """
        Insert closure table entries.
        
        Args:
            closure_entries: List of (ancestor, descendant, depth) tuples
        """
        cursor = self.conn.cursor()
        
        # Clear existing data
        cursor.execute("DELETE FROM closure_table")
        
        # Insert closure table entries
        for ancestor, descendant, depth in closure_entries:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO closure_table 
                    (ancestor, descendant, depth)
                    VALUES (?, ?, ?)
                """, (ancestor, descendant, depth))
            except sqlite3.IntegrityError:
                # Skip duplicates
                pass
        
        self.conn.commit()
    
    def get_statistics(self) -> dict:
        """
        Get database statistics.
        
        Returns:
            Dictionary with counts of nodes, segments, and closure entries
        """
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM nodos_circuito")
        nodos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM segmentos_circuito")
        segmentos_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM closure_table")
        closure_count = cursor.fetchone()[0]
        
        return {
            'nodos': nodos_count,
            'segmentos': segmentos_count,
            'closure_entries': closure_count
        }
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
