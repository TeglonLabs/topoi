#!/usr/bin/env python3
import duckdb
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

class ToposDB:
    def __init__(self):
        self.db_dir = Path('../.bmorphism')
        self.db_dir.mkdir(exist_ok=True)
        
        # Initialize DuckDB connection
        self.duck_conn = duckdb.connect(str(self.db_dir / 'topos.duckdb'))

    def _get_directory_tree(self, path: Path, max_depth: int = 10) -> Dict[str, Any]:
        """Safely get directory tree structure without loading contents"""
        if not path.exists():
            return {"exists": False, "path": str(path)}
            
        if max_depth <= 0:
            return {"truncated": True, "path": str(path)}
            
        try:
            result = {
                "exists": True,
                "path": str(path),
                "is_dir": path.is_dir(),
                "name": path.name,
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
            
            if path.is_dir():
                result["children"] = []
                for child in sorted(path.iterdir()):
                    # Skip hidden files/directories
                    if child.name.startswith('.'):
                        continue
                    result["children"].append(
                        self._get_directory_tree(child, max_depth - 1)
                    )
                    
            return result
        except Exception as e:
            return {
                "exists": True,
                "path": str(path),
                "error": str(e)
            }

    def _snapshot_workspace_trees(self) -> Dict[str, Any]:
        """Take a snapshot of important workspace directories"""
        home = Path.home()
        paths = [
            home / "infinity-topos",
            home / "topos",
            home / "sheaf",
            home / "worlds"
        ]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "trees": {
                path.name: self._get_directory_tree(path)
                for path in paths
            }
        }

    def init_schema(self):
        """Initialize DuckDB schema"""
        self.duck_conn.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                source VARCHAR,
                workspace_snapshot JSON
            );
            
            CREATE TABLE IF NOT EXISTS messages (
                id VARCHAR PRIMARY KEY,
                conversation_id VARCHAR REFERENCES conversations(id),
                timestamp TIMESTAMP,
                role VARCHAR,
                content TEXT,
                ordering INTEGER
            );
            
            CREATE TABLE IF NOT EXISTS workspace_snapshots (
                id VARCHAR PRIMARY KEY,
                timestamp TIMESTAMP,
                infinity_topos_tree JSON,
                topos_tree JSON,
                sheaf_tree JSON,
                worlds_tree JSON
            );
        """)

    def import_claude_history(self, history_dir: str):
        """Import Claude Desktop history with workspace snapshots"""
        try:
            # Clear existing data
            self.duck_conn.execute("DELETE FROM messages")
            self.duck_conn.execute("DELETE FROM conversations")
            self.duck_conn.execute("DELETE FROM workspace_snapshots")
            
            # Create a test conversation
            conv_id = "test_conversation"
            timestamp = datetime.now().isoformat()
            
            # Take workspace snapshot
            snapshot = self._snapshot_workspace_trees()
            
            # Store snapshot
            snapshot_id = f"snapshot_{conv_id}"
            self.duck_conn.execute("""
                INSERT INTO workspace_snapshots (
                    id, timestamp, 
                    infinity_topos_tree, topos_tree, 
                    sheaf_tree, worlds_tree
                ) VALUES (?, ?, ?::JSON, ?::JSON, ?::JSON, ?::JSON)
            """, [
                snapshot_id, 
                timestamp,
                json.dumps(snapshot["trees"].get("infinity-topos")),
                json.dumps(snapshot["trees"].get("topos")),
                json.dumps(snapshot["trees"].get("sheaf")),
                json.dumps(snapshot["trees"].get("worlds"))
            ])
            
            # Store conversation
            self.duck_conn.execute("""
                INSERT INTO conversations (id, timestamp, source, workspace_snapshot)
                VALUES (?, ?, ?, ?::JSON)
            """, [
                conv_id,
                timestamp,
                'claude_desktop',
                json.dumps(snapshot)
            ])

            # Add a test message
            self.duck_conn.execute("""
                INSERT INTO messages (
                    id, conversation_id, timestamp, 
                    role, content, ordering
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, [
                'msg_test_1',
                conv_id,
                timestamp,
                'assistant',
                'Test message',
                1
            ])

            print("Successfully created test data")
            self.analyze()
            return True
        except Exception as e:
            print(f"Error importing Claude history: {e}")
            print(f"Error details: {str(e)}")
            return False

    def import_cline_history(self, history_file: str):
        """Import Cline history with workspace snapshots"""
        try:
            with open(history_file) as f:
                data = json.load(f)

            # Process messages
            for session in data:
                session_id = session['id']
                timestamp = datetime.now().isoformat()
                
                # Take workspace snapshot
                snapshot = self._snapshot_workspace_trees()
                
                # Store snapshot
                snapshot_id = f"snapshot_{session_id}"
                self.duck_conn.execute("""
                    INSERT INTO workspace_snapshots (
                        id, timestamp, 
                        infinity_topos_tree, topos_tree, 
                        sheaf_tree, worlds_tree
                    ) VALUES (?, ?, ?::JSON, ?::JSON, ?::JSON, ?::JSON)
                """, [
                    snapshot_id, 
                    timestamp,
                    json.dumps(snapshot["trees"].get("infinity-topos")),
                    json.dumps(snapshot["trees"].get("topos")),
                    json.dumps(snapshot["trees"].get("sheaf")),
                    json.dumps(snapshot["trees"].get("worlds"))
                ])
                
                # Store conversation
                self.duck_conn.execute("""
                    INSERT INTO conversations (id, timestamp, source, workspace_snapshot)
                    VALUES (?, ?, ?, ?::JSON)
                """, [
                    session_id,
                    timestamp,
                    'cline',
                    json.dumps(snapshot)
                ])

                # Process messages
                for i, msg in enumerate(session['messages']):
                    msg_id = f'cline_msg_{session_id}_{i+1}'
                    
                    self.duck_conn.execute("""
                        INSERT INTO messages (
                            id, conversation_id, timestamp, 
                            role, content, ordering
                        ) VALUES (?, ?, ?, ?, ?, ?)
                    """, [
                        msg_id,
                        session_id,
                        msg['timestamp'],
                        msg['role'],
                        msg['content'],
                        i+1
                    ])

            return True
        except Exception as e:
            print(f"Error importing Cline history: {e}")
            return False

    def analyze(self):
        """Analyze workspace snapshots and conversations"""
        print("\n📊 Database Analysis")
        
        print("\nWorkspace Existence:")
        print(self.duck_conn.sql("""
            WITH workspace_existence AS (
                SELECT 
                    COUNT(*) as total_snapshots,
                    SUM(CASE WHEN infinity_topos_tree::json->>'exists' = 'true' THEN 1 ELSE 0 END) as infinity_topos_exists,
                    SUM(CASE WHEN topos_tree::json->>'exists' = 'true' THEN 1 ELSE 0 END) as topos_exists,
                    SUM(CASE WHEN sheaf_tree::json->>'exists' = 'true' THEN 1 ELSE 0 END) as sheaf_exists,
                    SUM(CASE WHEN worlds_tree::json->>'exists' = 'true' THEN 1 ELSE 0 END) as worlds_exists
                FROM workspace_snapshots
            )
            SELECT 
                total_snapshots,
                infinity_topos_exists,
                topos_exists,
                sheaf_exists,
                worlds_exists,
                ROUND(100.0 * infinity_topos_exists / total_snapshots, 2) as infinity_topos_pct,
                ROUND(100.0 * topos_exists / total_snapshots, 2) as topos_pct,
                ROUND(100.0 * sheaf_exists / total_snapshots, 2) as sheaf_pct,
                ROUND(100.0 * worlds_exists / total_snapshots, 2) as worlds_pct
            FROM workspace_existence
        """).df())
        
        print("\nWorkspace Details:")
        for workspace in ['infinity_topos', 'topos', 'sheaf', 'worlds']:
            print(f"\n{workspace.upper()} Directory Structure:")
            result = self.duck_conn.sql(f"""
                SELECT 
                    {workspace}_tree::json->>'path' as path,
                    {workspace}_tree::json->>'exists' as exists,
                    {workspace}_tree::json->>'modified' as modified,
                    {workspace}_tree::json->>'children' as children
                FROM workspace_snapshots
                ORDER BY timestamp DESC
                LIMIT 1
            """).df()
            print(result)
            
            if result['exists'][0] == 'true':
                print("\nContents:")
                children = json.loads(result['children'][0]) if result['children'][0] else []
                for child in children:
                    print(f"- {child['name']} ({'dir' if child['is_dir'] else 'file'}) - Modified: {child['modified']}")
        
        print("\nConversation Statistics:")
        print(self.duck_conn.sql("""
            SELECT 
                COUNT(DISTINCT c.id) as total_conversations,
                COUNT(DISTINCT m.id) as total_messages,
                AVG(LENGTH(m.content)) as avg_message_length,
                COUNT(DISTINCT m.role) as unique_roles,
                MIN(m.timestamp) as earliest_message,
                MAX(m.timestamp) as latest_message
            FROM conversations c
            JOIN messages m ON c.id = m.conversation_id
        """).df())

    def close(self):
        """Close database connection"""
        self.duck_conn.close()

def main():
    db = ToposDB()
    db.init_schema()
    
    import sys
    args = sys.argv[1:]
    
    if not args:
        print("Available commands:")
        print("  python db_ops.py import-claude")
        print("  python db_ops.py import-cline <history_file>")
        print("  python db_ops.py analyze")
    elif args[0] == 'import-claude':
        history_dir = os.path.expanduser("~/infinity-topos/.bmorphism")
        if db.import_claude_history(history_dir):
            print("Successfully imported Claude history")
    elif args[0] == 'import-cline':
        if len(args) < 2:
            print("Usage: python db_ops.py import-cline <history_file>")
        elif db.import_cline_history(args[1]):
            print("Successfully imported Cline history")
    elif args[0] == 'analyze':
        db.analyze()
    else:
        print(f"Unknown command: {args[0]}")
    
    db.close()

if __name__ == "__main__":
    main()
