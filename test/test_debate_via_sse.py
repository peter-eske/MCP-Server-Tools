import asyncio, json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

async def main():
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    server_url = "http://localhost:8000/sse"
    
    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            
            result = await session.call_tool("konsultiere_expertengruppe", {
                "problemstellung": "Was ist 2+2? Antworte kurz.",
                "experten_modelle": ["default"],
                "maximale_sekunden": 30
            })
            text = result.content[0].text
            print(f"\n=== DEBATTE ERGEBNIS (Auszug) ===\n{text[:1000]}")
            print(f"\n=== ENDE (Gesamtlänge: {len(text)} Zeichen) ===")

            return "OK" if "Fehler" not in text[:100] else f"FEHLER: {text[:200]}"

try:
    result = asyncio.run(main())
    print(f"\n=== TEST: {result} ===")
except Exception as e:
    import traceback
    print(f"\n=== TEST FEHLGESCHLAGEN: {e} ===")
    traceback.print_exc()
