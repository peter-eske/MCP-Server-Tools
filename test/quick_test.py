import asyncio, sys, time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

async def main():
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession

    async with sse_client("http://localhost:8000/sse") as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()

            t0 = time.time()
            result = await session.call_tool("konsultiere_expertengruppe", {
                "problemstellung": "Was ist 2+2?",
                "experten_modelle": ["default"],
                "maximale_sekunden": 30
            })
            elapsed = time.time() - t0
            text = result.content[0].text
            print(f"DAUER: {elapsed:.1f}s")
            print(f"LAENGE: {len(text)} Zeichen")
            print(f"ANFANG: {text[:200]}")
            print(f"ENDE:   {text[-200:]}")
            if "Fehler" in text[:100]:
                return f"FEHLER: {text[:300]}"
            return "OK" if len(text) > 50 else f"ZU KURZ: {text[:200]}"

try:
    r = asyncio.run(main())
    print(f"\nTEST: {r}")
except Exception as e:
    import traceback
    traceback.print_exc()
