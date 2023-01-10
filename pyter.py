import asyncio
import time
import requests
from aiohttp import ClientSession
from queue import PriorityQueue


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
    async with ClientSession(raise_for_status=True) as session:
        async with session.get(url, headers={"Range": f"bytes={start}-{end}"}) as response:
            await pieces.put((start, await response.read()))


async def manager(url: str, pieces: PriorityQueue, threads: int = 16):
    chunks = chop(url, threads)
    tasks = []

    for j in range(len(chunks) - 1):
        task = asyncio.create_task(
            download_file(url, pieces, chunks[j], chunks[j + 1] - 1)
        )

        tasks.append(task)

    await asyncio.gather(*tasks, return_exceptions=True)


url = "https://cdna.p30download.ir/p30dl-audio/Vangelis.Singles_p30download.com.rar"
# url = "https://files.realpython.com/media/What-is-the-Python-Global-Interpreter-Lock-GIL_Watermarked.0695d8c16efe.jpg"
pieces = PriorityQueue()

s1 = time.time()
asyncio.run(manager(url, pieces))
print(f"threaded: {time.time() - s1}")

s2 = time.time()
requests.get(url)
print(f"normal: {time.time() - s2}")


# with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "wb") as file:
#     while not pieces.empty():
#         file.write(pieces.get()[1])
