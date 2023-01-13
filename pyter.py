import requests
import asyncio
from argparse import ArgumentParser, Namespace
from pathlib import Path
from requests import Session
from aiohttp import ClientSession
from queue import PriorityQueue
from typing import Coroutine
from tqdm import trange
from tqdm.asyncio import tqdm_asyncio


async def download_file(url: str, start: int, end: int) -> Coroutine:
    async with ClientSession(raise_for_status=True) as session:
        async with session.get(url, headers={"Range": f"bytes={start}-{end}"}) as response:
            pieces.put((start, await response.read()))


async def manager(url: str, chunks: list[int]) -> Coroutine:
    tasks = [asyncio.ensure_future(asyncio.sleep(1))]

    for j in range(len(chunks) - 1):
        task = asyncio.ensure_future(
            download_file(url, chunks[j], chunks[j + 1] - 1)
        )

        tasks.append(task)

    await tqdm_asyncio.gather(*tasks, timeout=100, colour="#77C3EC", unit="kB")


def _file_size(url: str) -> int:
    response = Session().head(url)

    _test_connection(response)

    if "content-length" in response.headers:
        return int(response.headers["content-length"])

    return 0


def _chop(size: int, threads: int) -> list[int]:
    chunk = size // threads if size // threads != 0 else size
    chunks = []

    for i in range(0, size - chunk, chunk):
        chunks.append(i)
    chunks.append(size + 1)

    return chunks


def _getArgs() -> Namespace:
    parser = ArgumentParser(
        prog="Pyter",
        description="Multi-Threaded Mini Downloader.",
        epilog=""
    )

    parser.add_argument("url",
                        help="url of a file.")

    parser.add_argument("-t", "--threads",
                        help="number of threads. (default=16)")

    parser.add_argument("-td", "--target-directory",
                        help="save downloaded file to this directory.")

    return parser.parse_args()


def _test_connection(response: requests.Response) -> None:
    if response.status_code == requests.codes.ok:
        raise requests.exceptions.ConnectionError()


if __name__ == "__main__":
    DEFAULT_THREADS = 16

    args = _getArgs()

    url = args.url

    size = _file_size(url)

    tdir = Path(args.target_directory) if args.target_directory \
        else Path("/home/armin/Downloads/pyter")

    if not tdir.exists():
        tdir.mkdir()

    if size != 0:
        threads = args.threads - 1 if args.threads else DEFAULT_THREADS - 1

        chunks = _chop(size, threads)

        pieces = PriorityQueue()

        print("\n")
        asyncio.run(manager(url, chunks))

        print("\n")
        for chunk_size in trange(size // 1024, colour="#77C3EC", unit="kB"):
            with open(tdir / Path(url).name, "wb") as file:
                while not pieces.empty():
                    file.write(pieces.get()[1])

    else:
        result = requests.get(url)

        with open(tdir / Path(url).name, "wb") as file:
            file.write(result.content)

    print(f"\nFile saved to: {tdir}")
