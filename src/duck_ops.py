#!/usr/bin/env python3
import duckdb
import sys
import os
import json
import time
from pathlib import Path

DB_PATH = '../.bmorphism/topos.duckdb'
os.makedirs('../.bmorphism', exist_ok=True)

def create_hypergraph_tables(con):
    """Create tables for hypergraph storage if they don't exist"""
    con.execute("""
        CREATE TABLE IF NOT EXISTS vertices (
            id VARCHAR PRIMARY KEY,
            properties JSON
        );
        
        CREATE TABLE IF NOT EXISTS hyperedges (
            id VARCHAR PRIMARY KEY,
            edge_type VARCHAR,
            properties JSON
        );
        
        CREATE TABLE IF NOT EXISTS incidence (
            edge_id VARCHAR REFERENCES hyperedges(id),
            vertex_id VARCHAR REFERENCES vertices(id),
            role VARCHAR,
            ordering INTEGER,
            PRIMARY KEY (edge_id, vertex_id, role)
        );
    """)

def import_claude_desktop(con, history_dir):
    """Import Claude Desktop history from .bmorphism directory"""
    try:
        # Clear existing data
        con.execute("DELETE FROM incidence")
        con.execute("DELETE FROM vertices")
        con.execute("DELETE FROM hyperedges")
        
        # Create a temporary table for the raw data
        con.execute("""
            CREATE TEMP TABLE IF NOT EXISTS temp_claude_history AS
            SELECT * FROM read_json_auto(?)
        """, [str(Path(history_dir) / "anthropic-data-2025-01-19-22-13-28/conversations.json")])
        
        # Process each conversation into our hypergraph structure
        con.execute("""
            WITH conversation_data AS (
                SELECT 
                    json_extract_string(conv.value, '$.id') as conversation_id,
                    json_extract_string(msg.value, '$.timestamp')::TIMESTAMP as timestamp,
                    json_extract_string(msg.value, '$.role') as role,
                    json_extract_string(msg.value, '$.content') as content
                FROM temp_claude_history,
                UNNEST(json_extract(conversations, '$[*]')) AS conv(value),
                UNNEST(json_extract(conv.value, '$.messages[*]')) AS msg(value)
            )
            INSERT INTO vertices (id, properties)
            SELECT 
                'msg_' || conversation_id || '_' || row_number() over (partition by conversation_id order by timestamp),
                json_object('timestamp', timestamp, 'role', role, 'content', content)
            FROM conversation_data
        """)
        
        # Create hyperedges for conversations
        con.execute("""
            WITH conversation_vertices AS (
                SELECT DISTINCT 
                    json_extract_string(conv.value, '$.id') as conversation_id
                FROM temp_claude_history,
                UNNEST(json_extract(conversations, '$[*]')) AS conv(value)
            )
            INSERT INTO hyperedges (id, edge_type, properties)
            SELECT 
                'conversation_' || conversation_id,
                'conversation',
                json_object('source', 'claude_desktop')
            FROM conversation_vertices
        """)
        
        # Link messages to conversations in incidence table
        con.execute("""
            WITH msg_edges AS (
                SELECT 
                    'conversation_' || json_extract_string(conv.value, '$.id') as edge_id,
                    v.id as vertex_id,
                    row_number() over (partition by json_extract_string(conv.value, '$.id') order by json_extract(v.properties, '$.timestamp')) as msg_order
                FROM temp_claude_history,
                UNNEST(json_extract(conversations, '$[*]')) AS conv(value)
                JOIN vertices v ON v.id LIKE 'msg_' || json_extract_string(conv.value, '$.id') || '_%'
            )
            INSERT INTO incidence (edge_id, vertex_id, role, ordering)
            SELECT edge_id, vertex_id, 'message', msg_order
            FROM msg_edges
        """)
        
        con.execute("DROP TABLE temp_claude_history")
        return True
    except Exception as e:
        print(f"Error importing Claude Desktop history: {e}")
        return False

def import_cline_history(con, history_file):
    """Import Cline session history"""
    try:
        # Clear existing data
        con.execute("DELETE FROM incidence")
        con.execute("DELETE FROM vertices")
        con.execute("DELETE FROM hyperedges")
        
        # Create a temporary table for the raw data
        con.execute("""
            CREATE TEMP TABLE IF NOT EXISTS temp_cline_history AS
            SELECT * FROM read_json_auto(?)
        """, [history_file])
        
        # Process messages into vertices
        con.execute("""
            WITH message_data AS (
                SELECT 
                    t.id as session_id,
                    json_extract_string(msg.value, '$.timestamp')::TIMESTAMP as timestamp,
                    json_extract_string(msg.value, '$.role') as role,
                    json_extract_string(msg.value, '$.content') as content
                FROM temp_cline_history t,
                UNNEST(json_extract(t.messages, '$[*]')) AS msg(value)
            )
            INSERT INTO vertices (id, properties)
            SELECT 
                'cline_msg_' || session_id || '_' || row_number() over (partition by session_id order by timestamp),
                json_object('timestamp', timestamp, 'role', role, 'content', content)
            FROM message_data
        """)
        
        # Create hyperedges for sessions
        con.execute("""
            WITH session_vertices AS (
                SELECT DISTINCT id as session_id
                FROM temp_cline_history
            )
            INSERT INTO hyperedges (id, edge_type, properties)
            SELECT 
                'session_' || session_id,
                'session',
                json_object('source', 'cline')
            FROM session_vertices
        """)
        
        # Link messages to sessions
        con.execute("""
            WITH msg_edges AS (
                SELECT 
                    'session_' || t.id as edge_id,
                    v.id as vertex_id,
                    row_number() over (partition by t.id order by json_extract(v.properties, '$.timestamp')) as msg_order
                FROM temp_cline_history t
                JOIN vertices v ON v.id LIKE 'cline_msg_' || t.id || '_%'
            )
            INSERT INTO incidence (edge_id, vertex_id, role, ordering)
            SELECT edge_id, vertex_id, 'message', msg_order
            FROM msg_edges
        """)
        
        con.execute("DROP TABLE temp_cline_history")
        return True
    except Exception as e:
        print(f"Error importing Cline history: {e}")
        return False

def import_data(con, file_path):
    """Import data from various file formats"""
    ext = Path(file_path).suffix.lower()
    table_name = Path(file_path).stem
    
    if ext == '.csv':
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_csv_auto('{file_path}')")
    elif ext == '.parquet':
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_parquet('{file_path}')")
    elif ext == '.json':
        con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM read_json_auto('{file_path}')")
    else:
        print(f"Unsupported file format: {ext}")
        return False
    return True

def insert_interaction(con, context_data):
    """Insert an interaction hyperedge with context vertices"""
    # Generate unique IDs
    interaction_id = f"interaction_{int(time.time()*1000)}"
    context_id = f"context_{int(time.time()*1000)}"
    
    # Insert context vertex
    con.execute("""
        INSERT INTO vertices (id, properties)
        VALUES (?, ?::JSON)
    """, [context_id, json.dumps(context_data)])
    
    # Insert interaction hyperedge
    con.execute("""
        INSERT INTO hyperedges (id, edge_type, properties)
        VALUES (?, 'interaction', ?::JSON)
    """, [interaction_id, json.dumps({
        'timestamp': time.time(),
        'type': 'interaction'
    })])
    
    # Connect context to interaction
    con.execute("""
        INSERT INTO incidence (edge_id, vertex_id, role, ordering)
        VALUES (?, ?, 'context', 1)
    """, [interaction_id, context_id])
    
    return interaction_id, context_id

def main():
    try:
        con = duckdb.connect(DB_PATH)
        create_hypergraph_tables(con)
        
        args = sys.argv[1:]
        if not args:
            # Show database overview
            print("\n📊 Hypergraph Database Overview")
            print("\nVertices:")
            print(con.sql("SELECT COUNT(*) as vertex_count FROM vertices").df())
            print("\nHyperedges:")
            print(con.sql("SELECT edge_type, COUNT(*) as count FROM hyperedges GROUP BY edge_type").df())
            
            print("\n🔍 Available Tables:")
            tables = con.sql("SELECT table_name FROM information_schema.tables WHERE table_schema='main'").df()
            for table in tables['table_name']:
                print(f"\n📋 {table} schema:")
                print(con.sql(f"DESCRIBE {table}").df())
                print(f"\n📝 {table} preview (up to 5 rows):")
                print(con.sql(f"SELECT * FROM {table} LIMIT 5").df())
                
        elif args[0] == 'import':
            if len(args) < 2:
                print("Usage: just duck import <file_path>")
            else:
                success = import_data(con, args[1])
                if success:
                    print(f"Successfully imported {args[1]}")
                    
        elif args[0] == 'query':
            # Execute custom query
            query = ' '.join(args[1:])
            print(f"\nExecuting query: {query}")
            print(con.sql(query).df())
            
        elif args[0] == 'analyze':
            # Analyze hypergraph properties
            print("\n📈 Hypergraph Analysis")
            
            # Vertex degree distribution
            print("\nVertex Degree Distribution:")
            print(con.sql("""
                SELECT 
                    v.id,
                    COUNT(i.edge_id) as degree
                FROM vertices v
                LEFT JOIN incidence i ON v.id = i.vertex_id
                GROUP BY v.id
                ORDER BY degree DESC
                LIMIT 10
            """).df())
            
            # Edge size distribution
            print("\nHyperedge Size Distribution:")
            print(con.sql("""
                SELECT 
                    e.edge_type,
                    COUNT(DISTINCT i.vertex_id) as size,
                    COUNT(*) as count
                FROM hyperedges e
                JOIN incidence i ON e.id = i.edge_id
                GROUP BY e.edge_type, e.id
                ORDER BY size DESC
                LIMIT 10
            """).df())
            
        elif args[0] == 'interact':
            if len(args) < 2:
                print("Usage: just duck interact <json_file>")
                return
            try:
                with open(args[1], 'r') as f:
                    context_data = json.load(f)
                interaction_id, context_id = insert_interaction(con, context_data)
                print(f"Created interaction {interaction_id} with context {context_id}")
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error: {e}")
                
        elif args[0] == 'import-claude':
            history_dir = os.path.expanduser("~/infinity-topos/.bmorphism")
            if import_claude_desktop(con, history_dir):
                print("Successfully imported Claude Desktop history")
            
        elif args[0] == 'import-cline':
            if len(args) < 2:
                print("Usage: just duck import-cline <history_file>")
                return
            if import_cline_history(con, args[1]):
                print("Successfully imported Cline history")
                
        else:
            print("Available commands:")
            print("  just duck                   - Show database overview")
            print("  just duck import <file>     - Import generic data file")
            print("  just duck import-claude     - Import Claude Desktop history")
            print("  just duck import-cline <file> - Import Cline history file")
            print("  just duck query \"SQL\"      - Execute custom SQL query")
            print("  just duck analyze          - Show hypergraph metrics")
            print("  just duck interact <file>  - Insert interaction from JSON")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
