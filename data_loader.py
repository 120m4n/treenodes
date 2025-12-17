"""
CSV data loader for electrical network nodes and segments.
"""

import csv
from typing import List, Dict
from pathlib import Path
from models import Nodo, Segmento


class DataLoader:
    """Loads nodes and segments from CSV files."""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = Path(data_dir)
    
    def load_nodos(self, filename: str = 'nodos_circuito.csv') -> List[Nodo]:
        """
        Load nodes from CSV file.
        
        Args:
            filename: Name of the CSV file containing nodes
            
        Returns:
            List of Nodo objects
        """
        nodos = []
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nodos.append(Nodo.from_csv_row(row))
        
        return nodos
    
    def load_segmentos(self, filename: str = 'segmentos_circuito.csv') -> List[Segmento]:
        """
        Load segments from CSV file.
        
        Args:
            filename: Name of the CSV file containing segments
            
        Returns:
            List of Segmento objects
        """
        segmentos = []
        filepath = self.data_dir / filename
        
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                segmentos.append(Segmento.from_csv_row(row))
        
        return segmentos
    
    def load_all(self) -> tuple[List[Nodo], List[Segmento]]:
        """
        Load both nodes and segments.
        
        Returns:
            Tuple of (nodos, segmentos)
        """
        return self.load_nodos(), self.load_segmentos()
