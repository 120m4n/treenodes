"""
Data models for electrical network nodes and segments.
Based on CSV headers from nodos_circuito.csv and segmentos_circuito.csv
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Nodo:
    """
    Represents a node in the electrical network.
    Fields based on nodos_circuito.csv headers.
    """
    id_nodo: int
    nombre: str
    tipo: str
    voltaje_kv: float
    x: float
    y: float

    @classmethod
    def from_csv_row(cls, row: dict) -> 'Nodo':
        """Create a Nodo instance from a CSV row dictionary."""
        return cls(
            id_nodo=int(row['id_nodo']),
            nombre=str(row['nombre']),
            tipo=str(row['tipo']),
            voltaje_kv=float(row['voltaje_kv']),
            x=float(row['x']),
            y=float(row['y'])
        )


@dataclass
class Segmento:
    """
    Represents a segment (edge) in the electrical network.
    Fields based on segmentos_circuito.csv headers.
    """
    id_segmento: int
    id_circuito: str
    nodo_inicio: int
    nodo_fin: int
    longitud_m: float
    tipo_conductor: int
    capacidad_amp: int

    @classmethod
    def from_csv_row(cls, row: dict) -> 'Segmento':
        """Create a Segmento instance from a CSV row dictionary."""
        return cls(
            id_segmento=int(row['id_segmento']),
            id_circuito=str(row['id_circuito']),
            nodo_inicio=int(row['nodo_inicio']),
            nodo_fin=int(row['nodo_fin']),
            longitud_m=float(row['longitud_m']),
            tipo_conductor=int(row['tipo_conductor']),
            capacidad_amp=int(row['capacidad_amp'])
        )
