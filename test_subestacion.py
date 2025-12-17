"""
Test script to verify that BFS starts from Subestacion node.
"""

from network_builder import NetworkBuilder
from models import Nodo, Segmento

def test_find_subestacion_success():
    """Test finding a Subestacion node when it exists."""
    print("Test 1: Finding Subestacion node when it exists...")
    
    # Create a simple network with a Subestacion node
    builder = NetworkBuilder(use_networkx=True)
    nodos = [
        Nodo(id_nodo=1, nombre="N1", tipo="Subestacion", voltaje_kv=34.5, x=0.0, y=0.0),
        Nodo(id_nodo=2, nombre="N2", tipo="POSTE EN H", voltaje_kv=13.8, x=1.0, y=1.0),
        Nodo(id_nodo=3, nombre="N3", tipo="POSTE SENCILLO", voltaje_kv=13.8, x=2.0, y=2.0),
    ]
    segmentos = [
        Segmento(id_segmento=1, id_circuito="C1", nodo_inicio=1, nodo_fin=2, 
                longitud_m=100.0, tipo_conductor=1, capacidad_amp=200),
        Segmento(id_segmento=2, id_circuito="C1", nodo_inicio=2, nodo_fin=3, 
                longitud_m=150.0, tipo_conductor=1, capacidad_amp=200),
    ]
    
    builder.build_network(nodos, segmentos)
    
    try:
        subestacion_id = builder.find_subestacion_node()
        assert subestacion_id == 1, f"Expected node ID 1, got {subestacion_id}"
        print(f"   ✓ Found Subestacion node: {subestacion_id}")
        print("   ✓ Test passed!\n")
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}\n")
        return False


def test_find_subestacion_error():
    """Test that an error is raised when no Subestacion node exists."""
    print("Test 2: Error when no Subestacion node exists...")
    
    # Create a network without a Subestacion node
    builder = NetworkBuilder(use_networkx=True)
    nodos = [
        Nodo(id_nodo=1, nombre="N1", tipo="POSTE EN H", voltaje_kv=13.8, x=0.0, y=0.0),
        Nodo(id_nodo=2, nombre="N2", tipo="POSTE SENCILLO", voltaje_kv=13.8, x=1.0, y=1.0),
    ]
    segmentos = [
        Segmento(id_segmento=1, id_circuito="C1", nodo_inicio=1, nodo_fin=2, 
                longitud_m=100.0, tipo_conductor=1, capacidad_amp=200),
    ]
    
    builder.build_network(nodos, segmentos)
    
    try:
        subestacion_id = builder.find_subestacion_node()
        print(f"   ✗ Test failed: Expected ValueError but got node ID {subestacion_id}\n")
        return False
    except ValueError as e:
        expected_msg = "No se encontró un nodo con tipo='Subestacion'"
        if expected_msg in str(e):
            print(f"   ✓ Correctly raised ValueError: {e}")
            print("   ✓ Test passed!\n")
            return True
        else:
            print(f"   ✗ Test failed: Wrong error message: {e}\n")
            return False
    except Exception as e:
        print(f"   ✗ Test failed with unexpected exception: {e}\n")
        return False


def test_bfs_from_subestacion():
    """Test that BFS traversal works correctly from Subestacion node."""
    print("Test 3: BFS traversal from Subestacion node...")
    
    # Create a simple network with a Subestacion node
    builder = NetworkBuilder(use_networkx=True)
    nodos = [
        Nodo(id_nodo=1, nombre="Subestacion", tipo="Subestacion", voltaje_kv=34.5, x=0.0, y=0.0),
        Nodo(id_nodo=2, nombre="Poste1", tipo="POSTE EN H", voltaje_kv=13.8, x=1.0, y=1.0),
        Nodo(id_nodo=3, nombre="Poste2", tipo="POSTE SENCILLO", voltaje_kv=13.8, x=2.0, y=2.0),
        Nodo(id_nodo=4, nombre="Poste3", tipo="POSTE EN H", voltaje_kv=13.8, x=3.0, y=3.0),
    ]
    segmentos = [
        Segmento(id_segmento=1, id_circuito="C1", nodo_inicio=1, nodo_fin=2, 
                longitud_m=100.0, tipo_conductor=1, capacidad_amp=200),
        Segmento(id_segmento=2, id_circuito="C1", nodo_inicio=2, nodo_fin=3, 
                longitud_m=150.0, tipo_conductor=1, capacidad_amp=200),
        Segmento(id_segmento=3, id_circuito="C1", nodo_inicio=3, nodo_fin=4, 
                longitud_m=200.0, tipo_conductor=1, capacidad_amp=200),
    ]
    
    builder.build_network(nodos, segmentos)
    network = builder.get_network()
    
    try:
        subestacion_id = builder.find_subestacion_node()
        closure_entries = network.bfs_traversal(subestacion_id)
        
        # Verify we have closure entries
        assert len(closure_entries) > 0, "No closure entries generated"
        
        # Verify the root node (Subestacion) is in the closure table
        root_entries = [e for e in closure_entries if e[0] == subestacion_id and e[1] == subestacion_id]
        assert len(root_entries) == 1, "Root node should have one self-reference entry"
        
        # Verify all other nodes are descendants of Subestacion
        descendant_ids = set([e[1] for e in closure_entries if e[0] == subestacion_id and e[2] > 0])
        expected_descendants = {2, 3, 4}
        assert descendant_ids == expected_descendants, f"Expected descendants {expected_descendants}, got {descendant_ids}"
        
        print(f"   ✓ BFS generated {len(closure_entries)} closure entries")
        print(f"   ✓ All nodes are reachable from Subestacion")
        print("   ✓ Test passed!\n")
        return True
    except Exception as e:
        print(f"   ✗ Test failed: {e}\n")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Testing BFS Subestacion Node Requirements")
    print("=" * 60)
    print()
    
    results = []
    results.append(test_find_subestacion_success())
    results.append(test_find_subestacion_error())
    results.append(test_bfs_from_subestacion())
    
    print("=" * 60)
    print(f"Test Results: {sum(results)}/{len(results)} passed")
    print("=" * 60)
    
    if all(results):
        print("\n✓ All tests passed!")
        exit(0)
    else:
        print("\n✗ Some tests failed!")
        exit(1)
