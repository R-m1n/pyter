import asyncio
from typing import List
import aiohttp
import requests


url = "https://files.realpython.com/media/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg"


def file_size(url: str) -> int:
    return int(requests.Session().head(url).headers["content-length"])


def chop(url, threads):
    size = file_size(url)
    chunk = size // threads
    chunks = []

    for i in range(0, size - chunk, chunk):
        chunks.append(i)
    chunks.append(size + 1)

    return chunks


async def download_file(session: aiohttp.ClientSession, url: str, start: int, end: int, target) -> aiohttp.ClientResponse:
    print("///////")
    with session.get(url, headers={"Range": f"bytes={start}-{end}"}, stream=True) as response:
        with open(target, "xb") as file:
            for piece in response.content.iter_any():
                await file.write(piece)


async def save_file(response: aiohttp.ClientResponse, target: str):
    print("++++++")


async def handler(session, url, start, end, target: str) -> None:
    print("------")
    download_file(session, url, start, end, target)


async def manager(url: str, target: str, threads: int = 16):

    chunks = chop(url, threads)
    async with aiohttp.ClientSession() as session:
        tasks = []

        for j in range(len(chunks) - 1):
            task = asyncio.ensure_future(handler(
                session, url, chunks[j], chunks[j + 1] - 1, target))

            tasks.append(task)

        await asyncio.gather(*tasks, return_exceptions=True)


# threads = 16
# size = int(requests.head(url).headers["content-length"])
# chunk = size // threads
# chunks = []

# for i in range(0, size - chunk, chunk):
#     chunks.append(i)
# chunks.append(size + 1)

# pieces: List[requests.Response] = []
# for j in range(len(chunks) - 1):
#     piece = requests.get(
#         url, headers={"Range": f"bytes={chunks[j]}-{chunks[j + 1] - 1}"}, stream=True)

#     pieces.append(piece)

# with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "xb") as file:
#     for piece in pieces:
#         for chunk in piece.iter_content(chunk_size=128):
#             file.write(chunk)

asyncio.run(manager(
    url, "/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg"))
