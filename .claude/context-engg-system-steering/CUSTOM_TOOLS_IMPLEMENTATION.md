# Custom Tools Implementation for Sub-Agents

## Overview

While Claude Code doesn't natively support defining custom tools beyond the standard set, we can create custom tool functionality through several approaches.

## Approach 1: Shell Tool Wrapper Pattern

### Concept
Use the Shell tool to execute Python scripts that act as custom tools.

### Implementation

#### Step 1: Create Tool Script
```python
# .claude/tools/spec_tool.py
#!/usr/bin/env python3
"""Custom tool for spec management"""

import sys
import json
from pathlib import Path

class SpecTool:
    def create(self, name, description):
        """Create a new spec"""
        # Implementation
        return {"status": "created", "spec": name}
    
    def validate(self, spec_path):
        """Validate spec completeness"""
        # Implementation
        return {"valid": True, "issues": []}
    
    def generate_tasks(self, spec_path):
        """Generate tasks from spec"""
        # Implementation
        return {"tasks": [...]}

if __name__ == "__main__":
    tool = SpecTool()
    command = sys.argv[1]
    args = sys.argv[2:]
    
    result = getattr(tool, command)(*args)
    print(json.dumps(result))
```

#### Step 2: Create Agent with Custom Tool Access
```markdown
---
name: spec-manager
description: Manages specifications with custom tools
tools: Shell, Read, Write
---

You have access to custom spec management tools through Shell:

## Custom Tools Available

### SpecTool
Create specs: `Shell: python .claude/tools/spec_tool.py create {name} "{description}"`
Validate specs: `Shell: python .claude/tools/spec_tool.py validate {path}`
Generate tasks: `Shell: python .claude/tools/spec_tool.py generate_tasks {path}`

### MemoryTool
Store memory: `Shell: python .claude/tools/memory_tool.py store {key} "{value}"`
Retrieve memory: `Shell: python .claude/tools/memory_tool.py get {key}`
Search memories: `Shell: python .claude/tools/memory_tool.py search "{query}"`

When asked to create a spec, use:
```
Shell: python .claude/tools/spec_tool.py create {spec_name} "{description}"
```
```

## Approach 2: MCP (Model Context Protocol) Integration

### Concept
Create MCP servers that provide custom tools to Claude Code.

### Implementation

#### Step 1: Create MCP Server
```python
# .claude/mcp-servers/custom_tools_server.py
from mcp import Server, Tool, Resource

class CustomToolsServer(Server):
    def __init__(self):
        super().__init__("custom-tools")
        
        # Define custom tools
        self.register_tool(Tool(
            name="spec_create",
            description="Create a new specification",
            parameters={
                "name": "string",
                "description": "string"
            },
            handler=self.create_spec
        ))
        
        self.register_tool(Tool(
            name="memory_store",
            description="Store information in memory",
            parameters={
                "key": "string",
                "value": "any"
            },
            handler=self.store_memory
        ))
    
    async def create_spec(self, name: str, description: str):
        # Implementation
        return {"status": "created", "spec": name}
    
    async def store_memory(self, key: str, value: any):
        # Implementation
        return {"stored": True, "key": key}

if __name__ == "__main__":
    server = CustomToolsServer()
    server.run()
```

#### Step 2: Configure MCP Connection
```json
// .claude/mcp-config.json
{
  "servers": {
    "custom-tools": {
      "command": "python",
      "args": [".claude/mcp-servers/custom_tools_server.py"],
      "type": "stdio"
    }
  }
}
```

## Approach 3: Task Tool Extension Pattern

### Concept
Create pseudo-tools by having a special agent that acts as a tool provider.

### Implementation

#### Step 1: Create Tool Provider Agent
```markdown
---
name: tool-provider
description: Provides custom tool functionality to other agents
tools: Read, Write, Shell
---

You are a tool provider that executes custom tools when called via Task.

## Available Custom Tools

### SpecManagement.create(name, description)
Creates a new specification structure

### SpecManagement.validate(spec_path)
Validates specification completeness

### Memory.store(key, value)
Stores information in persistent memory

### Memory.retrieve(key)
Retrieves stored information

### Context.compress(text, max_tokens)
Compresses text to fit token limit

### Planning.analyze(tasks)
Analyzes tasks for parallel execution

When called with a tool request, execute the appropriate functionality and return results.
```

#### Step 2: Use from Other Agents
```markdown
---
name: my-agent
tools: Task, Read, Write
---

When you need custom tool functionality:

For spec creation:
Use Task tool to delegate to tool-provider:
Description: "SpecManagement.create('user-auth', 'User authentication system')"

For memory storage:
Use Task tool to delegate to tool-provider:
Description: "Memory.store('last_execution', {result})"
```

## Approach 4: Command Bridge Pattern

### Concept
Create commands that act as tools, callable through Shell.

### Implementation

#### Step 1: Create Tool Commands
```markdown
# .claude/commands/tool-spec-create.md
---
name: tool-spec-create
description: Tool for creating specifications
---

Run: python .claude/tools/spec_tool.py create {name} "{description}"
```

#### Step 2: Agent Uses Command as Tool
```markdown
---
name: my-agent
tools: Shell
---

Custom tools available via commands:
- Create spec: `Shell: claude-code /tool-spec-create {name} "{description}"`
- Validate spec: `Shell: claude-code /tool-spec-validate {path}`
```

## Recommended Custom Tools to Implement

### 1. SpecTool
- create(name, description)
- validate(spec_path)
- generate_tasks(spec_path)
- update_status(spec_name, status)

### 2. MemoryTool
- store(key, value)
- retrieve(key)
- search(query)
- get_similar(task)

### 3. ContextTool
- compress(text, max_tokens)
- extract_relevant(text, query)
- merge(context1, context2)
- validate(context)

### 4. PlanningTool
- analyze_dependencies(tasks)
- create_batches(tasks)
- estimate_time(task)
- optimize_sequence(tasks)

### 5. MonitoringTool
- track_start(task_id)
- track_end(task_id, result)
- get_metrics()
- alert(condition)

### 6. ValidationTool
- validate_code(file_path)
- validate_spec(spec_path)
- validate_requirements(req_path)
- check_completeness(artifact)

### 7. IntegrationTool
- call_api(endpoint, method, data)
- query_database(query)
- send_notification(message)
- trigger_webhook(url, payload)

## Implementation Example: Complete MemoryTool

```python
# .claude/tools/memory_tool.py
#!/usr/bin/env python3
"""Custom memory tool for agents"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime
import sys
import hashlib
from typing import Any, Dict, List

class MemoryTool:
    def __init__(self):
        self.db_path = Path('.claude/data/memory.db')
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize memory database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id TEXT PRIMARY KEY,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_key ON memories(key)
            """)
    
    def store(self, key: str, value: Any, agent: str = None) -> Dict:
        """Store a memory"""
        memory_id = hashlib.md5(f"{key}{datetime.now()}".encode()).hexdigest()
        value_json = json.dumps(value)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO memories (id, key, value, agent)
                VALUES (?, ?, ?, ?)
            """, (memory_id, key, value_json, agent))
        
        return {"stored": True, "id": memory_id, "key": key}
    
    def retrieve(self, key: str) -> Dict:
        """Retrieve a memory by key"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT value, timestamp, access_count 
                FROM memories 
                WHERE key = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (key,))
            
            row = cursor.fetchone()
            if row:
                # Update access count
                conn.execute("""
                    UPDATE memories 
                    SET access_count = access_count + 1 
                    WHERE key = ?
                """, (key,))
                
                return {
                    "found": True,
                    "value": json.loads(row[0]),
                    "timestamp": row[1],
                    "access_count": row[2]
                }
        
        return {"found": False, "key": key}
    
    def search(self, query: str, limit: int = 10) -> Dict:
        """Search memories by query"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, value, timestamp 
                FROM memories 
                WHERE key LIKE ? OR value LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (f"%{query}%", f"%{query}%", limit))
            
            results = []
            for row in cursor:
                results.append({
                    "key": row[0],
                    "value": json.loads(row[1]),
                    "timestamp": row[2]
                })
        
        return {"results": results, "count": len(results)}
    
    def get_recent(self, limit: int = 10) -> Dict:
        """Get recent memories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT key, value, timestamp, agent 
                FROM memories 
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            results = []
            for row in cursor:
                results.append({
                    "key": row[0],
                    "value": json.loads(row[1]),
                    "timestamp": row[2],
                    "agent": row[3]
                })
        
        return {"recent": results}

def main():
    """CLI interface for memory tool"""
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No command specified"}))
        sys.exit(1)
    
    tool = MemoryTool()
    command = sys.argv[1]
    
    try:
        if command == "store":
            if len(sys.argv) < 4:
                print(json.dumps({"error": "Usage: store <key> <value> [agent]"}))
                sys.exit(1)
            
            key = sys.argv[2]
            value = json.loads(sys.argv[3]) if sys.argv[3].startswith('{') else sys.argv[3]
            agent = sys.argv[4] if len(sys.argv) > 4 else None
            result = tool.store(key, value, agent)
            
        elif command == "retrieve":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: retrieve <key>"}))
                sys.exit(1)
            
            result = tool.retrieve(sys.argv[2])
            
        elif command == "search":
            if len(sys.argv) < 3:
                print(json.dumps({"error": "Usage: search <query>"}))
                sys.exit(1)
            
            result = tool.search(sys.argv[2])
            
        elif command == "recent":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = tool.get_recent(limit)
            
        else:
            result = {"error": f"Unknown command: {command}"}
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Usage in Agents

```markdown
---
name: enhanced-developer
description: Developer with custom tool access
tools: Shell, Read, Write
---

You have access to custom tools via Shell:

## Memory Operations
Store: `Shell: python .claude/tools/memory_tool.py store "key" '{"data": "value"}' developer`
Retrieve: `Shell: python .claude/tools/memory_tool.py retrieve "key"`
Search: `Shell: python .claude/tools/memory_tool.py search "query"`

## Spec Operations
Create: `Shell: python .claude/tools/spec_tool.py create {name} "{description}"`
Validate: `Shell: python .claude/tools/spec_tool.py validate {path}`

## Context Operations
Compress: `Shell: python .claude/tools/context_tool.py compress "{text}" {max_tokens}`
Extract: `Shell: python .claude/tools/context_tool.py extract "{text}" "{query}"`

Use these tools to enhance your capabilities beyond standard operations.
```

## Best Practices

1. **Tool Naming**: Use clear, action-oriented names
2. **Error Handling**: Always return structured errors
3. **Logging**: Log tool usage for debugging
4. **Validation**: Validate inputs before processing
5. **Documentation**: Document tool parameters clearly
6. **Testing**: Create tests for each tool
7. **Performance**: Cache frequent operations
8. **Security**: Sanitize inputs, especially for Shell execution

## Integration with Tool Bridge

The agent_tool_bridge.py can intercept these custom tool calls:

```python
class AgentToolBridge:
    def __init__(self):
        self.custom_tools = {
            'memory': MemoryTool(),
            'spec': SpecTool(),
            'context': ContextTool(),
            'planning': PlanningTool()
        }
    
    async def handle_custom_tool(self, tool_name: str, method: str, args: Dict):
        """Route custom tool calls"""
        if tool_name in self.custom_tools:
            tool = self.custom_tools[tool_name]
            return getattr(tool, method)(**args)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
```

## Conclusion

While Claude Code doesn't natively support custom tool definitions, we can effectively create custom tools through:
1. Shell wrapper scripts
2. MCP server integration
3. Tool provider agents
4. Command bridges

The Shell wrapper approach is recommended as it's simple, powerful, and integrates well with the existing system.