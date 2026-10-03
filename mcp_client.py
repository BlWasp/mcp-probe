#!/usr/bin/env python3
"""
MCP test client with command-line arguments.
Usage:
    python client.py list
    python client.py resource <uri>
    python client.py tool <name> --args '{"param": "value"}'
    python client.py prompt <name> --args '{"param": "value"}'
"""

import argparse
import asyncio
import base64
import json
import sys
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


def create_transport(url, username, password):
    """Create an HTTP transport with Basic authentication."""
    headers = {}
    if username and password:
        credentials = f"{username}:{password}"
        encoded_creds = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
        headers["Authorization"] = f"Basic {encoded_creds}"
    return StreamableHttpTransport(url=url, headers=headers)


async def cmd_list(client):
    """List all available prompts, resources, templates, and tools."""
    prompts = await client.list_prompts()
    resources = await client.list_resources()
    resource_templates = await client.list_resource_templates()
    tools = await client.list_tools()

    print("=" * 60)
    print("PROMPTS")
    print("=" * 60)
    if prompts:
        for p in prompts:
            print(f"\n  • {p.name}")
            if p.description:
                print(f"    {p.description.strip()}")
    else:
        print("  (none)")

    print("\n" + "=" * 60)
    print("RESOURCES")
    print("=" * 60)
    if resources:
        for r in resources:
            print(f"\n  • {r.name}")
            print(f"    URI : {r.uri!r}")
    else:
        print("  (none)")

    print("\n" + "=" * 60)
    print("RESOURCE TEMPLATES")
    print("=" * 60)
    if resource_templates:
        for rt in resource_templates:
            print(f"\n  • {rt.name}")
            print(f"    URI : {rt.uri!r}")
    else:
        print("  (none)")

    print("\n" + "=" * 60)
    print("TOOLS")
    print("=" * 60)
    if tools:
        for t in tools:
            params = list(t.inputSchema.get("properties", {}).keys())
            print(f"\n  • {t.name}({', '.join(params)})")
            if t.description:
                print(f"    {t.description.strip()}")
    else:
        print("  (none)")

    print()


async def cmd_resource(client, uri):
    """Read a resource by its URI."""
    try:
        result = await client.read_resource(uri)
        for item in result:
            if hasattr(item, "text"):
                print(item.text)
            else:
                print(item)
    except Exception as e:
        print(f"[-] Error reading resource: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_tool(client, name, args_dict):
    """Call a tool with arguments."""
    try:
        result = await client.call_tool(name, args_dict)
        for item in result:
            if hasattr(item, "text"):
                print(item.text)
            else:
                print(item)
    except Exception as e:
        print(f"[-] Error calling tool: {e}", file=sys.stderr)
        sys.exit(1)


async def cmd_prompt(client, name, args_dict):
    """Retrieve a prompt with arguments."""
    try:
        result = await client.get_prompt(name, args_dict)
        for msg in result.messages:
            if hasattr(msg.content, "text"):
                print(msg.content.text)
            else:
                print(msg.content)
    except Exception as e:
        print(f"[-] Error retrieving prompt: {e}", file=sys.stderr)
        sys.exit(1)


async def main():
    parser = argparse.ArgumentParser(
        description="MCP test client with CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s resource "resource://debug"
  %(prog)s tool query --args '{"id": "1"}'
  %(prog)s prompt get_items --args '{"text": "Hello World!"}'
        """
    )

    parser.add_argument(
        "--url",
        default="http://mcp.domain.local:8000/mcp/",
        help="MCP endpoint URL (default: %(default)s)"
    )
    parser.add_argument(
        "--username",
        default="mcp_user",
        help="Username for Basic authentication"
    )
    parser.add_argument(
        "--password",
        default="mcp_password",
        help="Password for Basic authentication"
    )

    subparsers = parser.add_subparsers(dest="command", help="Available command")

    # list
    subparsers.add_parser("list", help="List prompts, resources, templates, and tools")

    # resource
    parser_resource = subparsers.add_parser("resource", help="Read a resource")
    parser_resource.add_argument("uri", help="Resource URI (e.g. resource://debug)")

    # tool
    parser_tool = subparsers.add_parser("tool", help="Call a tool")
    parser_tool.add_argument("name", help="Tool name")
    parser_tool.add_argument(
        "--args",
        default="{}",
        help='JSON arguments (e.g. \'{"id": "1"}\')'
    )

    # prompt
    parser_prompt = subparsers.add_parser("prompt", help="Retrieve a prompt")
    parser_prompt.add_argument("name", help="Prompt name")
    parser_prompt.add_argument(
        "--args",
        default="{}",
        help='JSON arguments (e.g. \'{"text": "Hello"}\')'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    transport = create_transport(args.url, args.username, args.password)
    client = Client(transport)

    async with client:
        if args.command == "list":
            await cmd_list(client)
        elif args.command == "resource":
            await cmd_resource(client, args.uri)
        elif args.command == "tool":
            try:
                tool_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"[-] Invalid JSON in --args: {e}", file=sys.stderr)
                sys.exit(1)
            await cmd_tool(client, args.name, tool_args)
        elif args.command == "prompt":
            try:
                prompt_args = json.loads(args.args)
            except json.JSONDecodeError as e:
                print(f"[-] Invalid JSON in --args: {e}", file=sys.stderr)
                sys.exit(1)
            await cmd_prompt(client, args.name, prompt_args)


if __name__ == "__main__":
    asyncio.run(main())
