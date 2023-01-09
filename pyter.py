import asyncio
from typing import List
import aiohttp
import requests


url = "https://files.realpython.com/media/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg"


async def file_size(session: aiohttp.ClientSession, url: str) -> int:
    async with session.head(url) as response:
        return response.content_length


async def download_file(session: aiohttp.ClientSession, url: str, start: int, end: int) -> aiohttp.ClientResponse:
    async with session.get(url, headers={"Range": f"bytes={start}-{end}"}, stream=True) as response:
        return response


async def manager(url, threads: int = 16):
    async with aiohttp.ClientSession() as session:
        size = file_size(session, url)
        chunk = size // threads
        chunks = []

        for i in range(0, size - chunk, chunk):
            chunks.append(i)
        chunks.append(size)

        tasks = []

        for j in range(len(chunks) - 1):
            task = asyncio.ensure_future(download_file(
                session, url, chunks[j], chunks[j + 1]))
            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)


threads = 16
size = int(requests.head(url).headers["content-length"])
chunk = size // threads
chunks = []

for i in range(0, size - chunk, chunk):
    chunks.append(i)
chunks.append(size + 1)

pieces: List[requests.Response] = []
for j in range(len(chunks) - 1):

    piece = requests.get(
        url, headers={"Range": f"bytes={chunks[j]}-{chunks[j + 1] - 1}"}, stream=True)

    pieces.append(piece)

with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "xb") as file:
    for piece in pieces:
        for chunk in piece.iter_content(chunk_size=128):
            file.write(chunk)
