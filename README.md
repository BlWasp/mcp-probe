# MCP Probe

A command-line MCP (Model Context Protocol) client built with Python and `fastmcp`. It supports Basic HTTP authentication and provides subcommands to list, read, and interact with MCP servers.

## Features

- **Basic HTTP Authentication**: configurable username and password.
- **Four subcommands:**
  - `list`: list all available prompts, resources, resource templates, and tools.
  - `resource`: read a resource by its URI.
  - `tool`: call a tool with JSON arguments.
  - `prompt`: retrieve a prompt with JSON arguments.
- **JSON argument parsing** for tools and prompts via `--args`.
- **Configurable endpoint** via CLI flags.

## Requirements

- Python 3.8+
- `fastmcp`

Install dependencies:

```bash
pip install fastmcp
```

## Usage

```bash
python mcp_client.py <command> [options]
```

### Global Options

| Option | Default | Description |
|--------|---------|-------------|
| `--url` | `http://mcp.domain.local:8000/mcp/` | MCP server endpoint URL |
| `--username` | `mcp_user` | Username for Basic authentication |
| `--password` | `mcp_password` | Password for Basic authentication |

### Commands

#### `list`

List all available prompts, resources, resource templates, and tools.

```bash
python mcp_client.py list
```

#### `resource <uri>`

Read a resource by its URI.

```bash
python mcp_client.py resource "resource://debug"
python mcp_client.py resource "debug://status"
```

#### `tool <name> --args '<json>'`

Call a tool with JSON arguments.

```bash
python mcp_client.py tool query --args '{"id": "1"}'
python mcp_client.py tool search_message --args '{"query": "hello"}'
```

#### `prompt <name> --args '<json>'`

Retrieve a prompt with JSON arguments.

```bash
python mcp_client.py prompt get_items --args '{"text": "Hello World!"}'
```

## Examples

### List everything on a custom server

```bash
python mcp_client.py list --url http://mcp.domain.local:8000/mcp/ --username user --password P@ssword
```

### Read a debug resource

```bash
python mcp_client.py resource "debug://status" --url http://mcp.domain.local:8000/mcp/ --username user --password P@ssword
```

### Call a tool with arguments

```bash
python mcp_client.py tool pw_reset --args '{"username": "csv"}' --url http://mcp.domain.local:8000/mcp/ --username user --password P@ssword
```

### Retrieve a prompt

```bash
python mcp_client.py prompt get_items --args '{"text": "Hello World!"}' --url http://mcp.domain.local:8000/mcp/ --username user --password P@ssword
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `1` | Error (invalid JSON, resource/tool/prompt not found, connection error, etc.) |

## Notes

- The `--args` parameter must be a valid JSON object. Use single quotes around the JSON string to avoid shell escaping issues.
- The client uses `StreamableHttpTransport` from `fastmcp` for HTTP-based MCP communication.
- Credentials are sent via the `Authorization: Basic <base64>` header.
