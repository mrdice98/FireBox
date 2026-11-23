# FireBox Plugins & MCP Integration Guide

FireBox provides an extensible architecture supporting both native Python plugins and Model Context Protocol (MCP) clients.

---

## 1. Native Plugin Architecture

Plugins reside in `~/.firebox/plugins/<plugin-id>/` or `.firebox/plugins/`.

### Creating a Plugin
A FireBox plugin consists of:
1. `plugin.json` (Manifest):
   ```json
   {
     "id": "my_custom_tools",
     "name": "Custom DevOps Tools",
     "version": "1.0.0",
     "description": "Docker and Kubernetes helper tools"
   }
   ```
2. `plugin.py` (Implementation):
   ```python
   from firebox.tools.base import BaseTool, ToolResult

   class DockerPsTool(BaseTool):
       name = "docker_ps"
       description = "List running docker containers."
       category = "devops"

       def get_parameters_schema(self):
           return {"type": "object", "properties": {}}

       def run(self, **kwargs):
           import subprocess
           res = subprocess.run(["docker", "ps"], capture_output=True, text=True)
           return ToolResult(output=res.stdout, success=(res.returncode == 0))

   def get_tools():
       return [DockerPsTool()]
   ```

---

## 2. Model Context Protocol (MCP) Integration

FireBox can connect directly to stdio-based MCP servers and expose their tools to the agent engine.

### Configuring MCP Servers
Add server definitions in `~/.firebox/mcp.json`:
```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "app.db"],
      "enabled": true
    },
    "fetch": {
      "command": "uvx",
      "args": ["mcp-server-fetch"],
      "enabled": true
    }
  }
}
```

When FireBox starts, it automatically queries tools from all enabled MCP servers, wraps them into native `BaseTool` instances, and exposes them to the active model.
