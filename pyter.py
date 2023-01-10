import asyncio
from requests import Session
from aiohttp import ClientSession
from queue import PriorityQueue
from typing import Coroutine


async def download_file(url: str, start: int, end: int) -> Coroutine:
    async with ClientSession(raise_for_status=True) as session:
        async with session.get(url, headers={"Range": f"bytes={start}-{end}"}) as response:
            pieces.put((start, await response.read()))


async def manager(url: str, chunks: list[int]) -> Coroutine:
    tasks = []

    for j in range(len(chunks) - 1):
        task = asyncio.ensure_future(
            download_file(url, chunks[j], chunks[j + 1] - 1)
        )

        tasks.append(task)

    await asyncio.gather(*tasks)


def _file_size(url: str) -> int:
    return int(Session().head(url).headers["content-length"])


def _chop(url: str, threads: int) -> list[int]:
    size = _file_size(url)
    chunk = size // threads
    chunks = []

    for i in range(0, size - chunk, chunk):
        chunks.append(i)
    chunks.append(size + 1)

    return chunks


if __name__ == "__main__":
    url = "https://cdna.p30download.ir/p30dl-audio/2Cellos.2011.2Cellos_p30download.com.rar"
    # url = "https://files.realpython.com/media/What-is-the-Python-Global-Interpreter-Lock-GIL_Watermarked.0695d8c16efe.jpg"

    threads = 16
    chunks = _chop(url, threads)
    pieces = PriorityQueue()

    # asyncio.run(manager(url, chunks))

    # with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "wb") as file:
    #     while not pieces.empty():
    #         file.write(pieces.get()[1])
