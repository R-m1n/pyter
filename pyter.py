import asyncio
import aiohttp
import requests
from queue import PriorityQueue


url = "https://files.realpython.com/media/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg"
# pieces = []


def file_size(url: str) -> int:
    return int(requests.Session().head(url).headers["content-length"])


def chop(url: str, threads: int):
    size = file_size(url)
    chunk = size // threads
    chunks = []

    for i in range(0, size - chunk, chunk):
        chunks.append(i)
    chunks.append(size + 1)

    return chunks


async def download_file(url: str, pieces: PriorityQueue, start: int, end: int) -> None:
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url, headers={"Range": f"bytes={start}-{end}"}) as response:
            await pieces.put((start, await response.read()))


async def manager(url: str, pieces: PriorityQueue, threads: int = 16):
    chunks = chop(url, threads)
    tasks = []

    for j in range(len(chunks) - 1):
        task = asyncio.ensure_future(
            download_file(url, pieces, chunks[j], chunks[j + 1] - 1)
        )

        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)


# threads = 16
# size = int(requests.head(url).headers["content-length"])
# chunk = size // threads
# chunks = []

# for i in range(0, size - chunk, chunk):
#     chunks.append(i)
# chunks.append(size + 1)

# pieces: List[requests.responseonse] = []
# for j in range(len(chunks) - 1):
#     piece = requests.get(
#         url, headers={"Range": f"bytes={chunks[j]}-{chunks[j + 1] - 1}"}, stream=True)

#     pieces.append(piece)

# with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "xb") as file:
#     for piece in pieces:
#         for chunk in piece.iter_content(chunk_size=128):
#             file.write(chunk)

# async def test():
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url) as resp:
#             if resp.status == 200:
#                 f = await aiofiles.open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", mode='wb')
#                 await f.write(await resp.read())
#                 await f.close()


# asyncio.run(test())

pieces = PriorityQueue()
asyncio.run(manager(url, pieces))

with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "wb") as file:
    while not pieces.empty():
        file.write(pieces.get()[1])
