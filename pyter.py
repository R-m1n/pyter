import requests
import asyncio
import aiohttp
import sys
import tqdm
import os
from argparse import ArgumentParser, Namespace
from pathlib import Path
from queue import PriorityQueue
from typing import Coroutine
from tqdm.asyncio import tqdm_asyncio


async def download_file(url: str, start: int, end: int) -> Coroutine:
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        async with session.get(url, headers={"Range": f"bytes={start}-{end}"}) as response:
            pieces.put((start, await response.read()))


async def manager(url: str, chunks: list[int]) -> Coroutine:
    tasks = []

    for j in range(len(chunks) - 1):
        task = asyncio.ensure_future(
            download_file(url, chunks[j], chunks[j + 1] - 1)
        )

        tasks.append(task)

    await tqdm_asyncio.gather(*tasks, colour=LIGHT_BLUE, unit="kB")


def _file_size(session: requests.Session, url: str) -> int:
    response = session.head(url)

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
                        help="URL of a file.")

    parser.add_argument("-t", "--threads",
                        help="number of threads. (default=16)")

    parser.add_argument("-td", "--target-directory",
                        help="save downloaded file to this directory.")

    return parser.parse_args()


def _test_connection(session: requests.Session, url: str) -> None:
    if session.head(url).status_code != requests.codes.ok:
        raise requests.exceptions.ConnectionError()


def _set_default_tdir() -> Path:
    platform = sys.platform
    user = os.getlogin()

    if platform == "linux":     # Linux
        return Path(f"/home/{user}/Downloads/pyter")

    elif platform == "win32":   # Windows
        return Path(f"C:\\Users\\{user}\\Downloads\\pyter")

    elif platform == "darwin":  # Mac OS X
        return Path(f"/Users/{user}/Downloads/pyter")


if __name__ == "__main__":
    DEFAULT_THREADS = 16
    DEFAULT_TDIR = _set_default_tdir()
    LIGHT_BLUE = "#77C3EC"

    args = _getArgs()

    url = args.url

    with requests.Session() as session:
        try:
            _test_connection(session, url)

        except requests.exceptions.ConnectionError:
            print("Connection failed!, Please try another time.")
            sys.exit()

        size = _file_size(session, url)

        size_in_kb = size // 1024

    tdir = Path(args.target_directory) if args.target_directory \
        else DEFAULT_TDIR

    if not tdir.exists():
        tdir.mkdir()

    if size != 0:
        threads = args.threads if args.threads else DEFAULT_THREADS

        chunks = _chop(size, threads)

        pieces = PriorityQueue()

        print("Downloadig...")
        asyncio.run(manager(url, chunks))

        print(f"\nSaving file to {tdir}")
        for chunk_size in tqdm.trange(size_in_kb, colour=LIGHT_BLUE, unit="kB"):
            with open(tdir / Path(url).name, "wb") as file:
                while not pieces.empty():
                    file.write(pieces.get()[1])

    else:
        result = requests.get(url)

        with open(tdir / Path(url).name, "wb") as file:
            file.write(result.content)
