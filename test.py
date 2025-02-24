import asyncio
from pathlib import Path

from rtfm_lookup import RtfmManager

data = Path("data")


async def main():
    async with RtfmManager() as rtfm:
        # await rtfm.get_manual("test", "https://rtfm.cibere.dev/stable/")
        rtfm.import_(data.read_bytes())

        async for entry in rtfm["test"].query("doc"):
            print(f"{entry.text} - {entry.url}")

        data.write_bytes(rtfm.export("json"))


asyncio.run(main())
