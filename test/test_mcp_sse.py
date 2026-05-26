import asyncio, json, sys

async def main():
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    server_url = "http://localhost:8000/sse"
    print(f"Verbinde zu MCP Server (SSE): {server_url}")

    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            print("Initialize: OK")

            tools = await session.list_tools()
            print(f"\nGefundene Tools ({len(tools.tools)}):")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description[:80]}")

            result = await session.call_tool("liste_verfuegbare_modelle", {})
            text = result.content[0].text
            print(f"\nliste_verfuegbare_modelle:\n{text[:600]}")

            return "OK" if "Fehler" not in text else f"FEHLER: {text[:200]}"

try:
    result = asyncio.run(main())
    print(f"\n=== TEST: {result} ===")
except Exception as e:
    import traceback
    print(f"\n=== TEST FEHLGESCHLAGEN: {e} ===")
    traceback.print_exc()
