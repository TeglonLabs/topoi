#!/usr/bin/env python3

from typing import Any, Dict, List, Optional, Set, Tuple, Union
import json
import networkx as nx
import discopy as dc
import kuzu
import duckdb
import shapely.geometry as geom
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

@dataclass
class HyperEdge:
    """A hyperedge connecting multiple vertices with optional attributes"""
    vertices: Set[str]
    attributes: Dict[str, Any] = field(default_factory=dict)
    geometry: Optional[geom.base.BaseGeometry] = None

class HyperGraphBackend(ABC):
    """Abstract base class for hypergraph backends"""
    
    @abstractmethod
    def add_vertex(self, vertex_id: str, **attrs) -> None:
        pass
    
    @abstractmethod
    def add_edge(self, edge: HyperEdge) -> None:
        pass
    
    @abstractmethod
    def get_neighbors(self, vertex_id: str) -> Set[str]:
        pass

class NetworkXBackend(HyperGraphBackend):
    """NetworkX-based implementation"""
    
    def __init__(self):
        self.graph = nx.Graph()
        
    def add_vertex(self, vertex_id: str, **attrs):
        self.graph.add_node(vertex_id, **attrs)
        
    def add_edge(self, edge: HyperEdge):
        # Convert hyperedge to clique
        vertices = list(edge.vertices)
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                self.graph.add_edge(vertices[i], vertices[j], 
                                  **edge.attributes)
                
    def get_neighbors(self, vertex_id: str) -> Set[str]:
        return set(self.graph.neighbors(vertex_id))

class DisCoPyBackend(HyperGraphBackend):
    """DisCoPy categorical implementation"""
    
    def __init__(self):
        self.diagram = dc.Diagram.id(dc.Ty())
        self.vertices = {}
        
    def add_vertex(self, vertex_id: str, **attrs):
        ty = dc.Ty(vertex_id)
        self.vertices[vertex_id] = ty
        self.diagram = self.diagram @ dc.Box(vertex_id, dc.Ty(), ty)
        
    def add_edge(self, edge: HyperEdge):
        # Create morphism between vertices
        dom = dc.Ty().tensor(*[self.vertices[v] for v in edge.vertices])
        cod = dc.Ty()
        self.diagram = self.diagram @ dc.Box(str(edge.attributes), dom, cod)
        
    def get_neighbors(self, vertex_id: str) -> Set[str]:
        # Get connected vertices through diagram composition
        connected = set()
        for box in self.diagram.boxes:
            if vertex_id in str(box.dom):
                for ty in box.dom:
                    if str(ty) != vertex_id:
                        connected.add(str(ty))
        return connected

class KuzuBackend(HyperGraphBackend):
    """Kuzu graph database backend"""
    
    def __init__(self, db_path: str):
        self.db = kuzu.Database(db_path)
        self.session = self.db.create_session()
        # Create schema
        self.session.run("CREATE NODE TABLE IF NOT EXISTS vertices(id STRING PRIMARY KEY, data STRING)")
        self.session.run("CREATE REL TABLE IF NOT EXISTS edges(FROM vertices TO vertices, data STRING)")
        
    def add_vertex(self, vertex_id: str, **attrs):
        self.session.run("INSERT INTO vertices VALUES ($1, $2)", 
                        [vertex_id, str(attrs)])
        
    def add_edge(self, edge: HyperEdge):
        # Convert hyperedge to multiple binary edges
        vertices = list(edge.vertices)
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                self.session.run("INSERT INTO edges VALUES ($1, $2, $3)",
                               [vertices[i], vertices[j], str(edge.attributes)])
                
    def get_neighbors(self, vertex_id: str) -> Set[str]:
        result = self.session.run("MATCH (v1:vertices)-[e:edges]-(v2:vertices) WHERE v1.id = $1 RETURN v2.id",
                                [vertex_id])
        return {row[0] for row in result}

class DuckDBBackend(HyperGraphBackend):
    """DuckDB spatial-enabled backend"""
    
    def __init__(self, db_path: str):
        self.con = duckdb.connect(db_path)
        # Create tables with spatial support using WKT
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS vertices (
                id VARCHAR PRIMARY KEY,
                data JSON,
                geom VARCHAR  -- Store as WKT
            )
        """)
        self.con.execute("""
            CREATE TABLE IF NOT EXISTS edges (
                id INTEGER PRIMARY KEY,
                vertices JSON,
                data JSON,
                geom VARCHAR  -- Store as WKT
            )
        """)
        
    def add_vertex(self, vertex_id: str, **attrs):
        geom = attrs.pop('geometry', None)
        self.con.execute("""
            INSERT INTO vertices (id, data, geom)
            VALUES (?, ?, ?)
        """, [vertex_id, json.dumps(attrs), str(geom) if geom else None])
        
    def add_edge(self, edge: HyperEdge):
        self.con.execute("""
            INSERT INTO edges (vertices, data, geom)
            VALUES (?, ?, ?)
        """, [json.dumps(list(edge.vertices)), json.dumps(edge.attributes), 
              str(edge.geometry) if edge.geometry else None])
        
    def get_neighbors(self, vertex_id: str) -> Set[str]:
        result = self.con.execute("""
            SELECT DISTINCT unnest(e.vertices) as neighbor
            FROM edges e
            WHERE array_contains(e.vertices, ?)
            AND unnest(e.vertices) != ?
        """, [vertex_id, vertex_id]).fetchall()
        return {row[0] for row in result}
    
    def get_vertex(self, vertex_id: str) -> Optional[Dict]:
        """Get vertex data by ID"""
        result = self.con.execute("""
            SELECT data
            FROM vertices
            WHERE id = ?
        """, [vertex_id]).fetchone()
        return json.loads(result[0]) if result else None

    def spatial_query(self, geom: geom.base.BaseGeometry) -> List[Tuple[str, Dict]]:
        """Query vertices/edges that intersect with given geometry"""
        vertices = self.con.execute("""
            SELECT id, data
            FROM vertices
            WHERE geom IS NOT NULL 
            AND geom = ?
        """, [str(geom)]).fetchall()
        
        edges = self.con.execute("""
            SELECT vertices, data
            FROM edges
            WHERE geom IS NOT NULL 
            AND geom = ?
        """, [str(geom)]).fetchall()
        
        return [(v[0], json.loads(v[1])) for v in vertices] + \
               [(str(e[0]), json.loads(e[1])) for e in edges]

class HyperGraph:
    """Main hypergraph interface combining multiple backends"""
    
    def __init__(self):
        self.backends = {
            'networkx': NetworkXBackend(),
            'discopy': DisCoPyBackend(),
            'kuzu': KuzuBackend('hypergraph.kuzu'),
            'duckdb': DuckDBBackend('hypergraph.duckdb')
        }
        
    def add_vertex(self, vertex_id: str, **attrs):
        """Add vertex to all backends"""
        for backend in self.backends.values():
            backend.add_vertex(vertex_id, **attrs)
            
    def add_edge(self, vertices: Set[str], **attrs):
        """Add hyperedge to all backends"""
        geom = attrs.pop('geometry', None)
        edge = HyperEdge(vertices, attrs, geom)
        for backend in self.backends.values():
            backend.add_edge(edge)
            
    def get_neighbors(self, vertex_id: str) -> Dict[str, Set[str]]:
        """Get neighbors from all backends"""
        return {name: backend.get_neighbors(vertex_id)
                for name, backend in self.backends.items()}
    
    def spatial_query(self, geom: geom.base.BaseGeometry) -> List[Tuple[str, Dict]]:
        """Perform spatial query using DuckDB backend"""
        return self.backends['duckdb'].spatial_query(geom)
