import asyncio
from requests import Response, Session


url = "https://files.realpython.com/media/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg"


def file_size(url: str, session: Session) -> int:
    return int(session.head(url).headers["content-length"])


def download_file(url: str, session: Session, start: int, end: int) -> Response:
    return session.get(url, headers={"Range": f"bytes={start}-{end}"}, stream=True)


with Session() as session:
    size = file_size(url, session)
    res = download_file(url, session, 1, size // 16)

res.raise_for_status()

# with open("/home/armin/Downloads/f/How-to-Run-A-Python-Script_Watermarked.65fe32bf5487.jpg", "xb") as file:
#     file.tell()
#     for chunk in res.iter_content(chunk_size=128):
#         file.write(chunk)
