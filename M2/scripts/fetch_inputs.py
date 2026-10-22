"""
Check 2 inputs: extract only the authors' files we need from the Zenodo v1.0 zip (5.9 GB) using HTTP range
requests, so the whole zip is never downloaded. Files keep their paths inside the zip.
"""
import hashlib
import io
import json
import time
import urllib.error
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

RECORD = "15209118"
OUT = Path("M2/inputs/zenodo")
PROJECT_FILES = ["ordered_refactorings.csv", "proneness_results.csv", "bcp_proneness_results.csv"]


def get(request):
    # urlopen with retries on HTTP 429 (Zenodo rate limit
    for attempt in range(8):
        try:
            return urllib.request.urlopen(request).read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            wait = int(e.headers.get("Retry-After") or 2 ** (attempt + 2))
            print(f"  rate limited, waiting {wait}s", flush=True)
            time.sleep(wait)
    raise RuntimeError("Zenodo kept rate-limiting; re-run later (finished files are kept)")


class HttpRangeFile(io.RawIOBase):
    """only downloads the parts it needs.
    Reads ahead in 4 MB blocks and retries on code 429(stay under Zenodo's rate limit)"""

    BLOCK = 4 * 1024 * 1024

    def __init__(self, url, size):
        self.url, self.size, self.pos = url, size, 0
        self.buf_start, self.buf = 0, b""

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=0):
        self.pos = {0: offset, 1: self.pos + offset, 2: self.size + offset}[whence]
        return self.pos

    def _fetch(self, start, end):
        return get(urllib.request.Request(self.url, headers={"Range": f"bytes={start}-{end - 1}"}))

    def read(self, n=-1):
        end = self.size if n < 0 else min(self.pos + n, self.size)
        if self.pos >= end:
            return b""
        if not (self.buf_start <= self.pos and end <= self.buf_start + len(self.buf)):
            self.buf_start = self.pos
            self.buf = self._fetch(self.pos, min(max(end, self.pos + self.BLOCK), self.size))
        data = self.buf[self.pos - self.buf_start:end - self.buf_start]
        self.pos += len(data)
        return data


sample = pd.read_csv("M2/inputs/sample_cases.csv")
sample["project"] = sample["class_id"].str.extract(r"^\d+_\d+_[a-z-]+?_(.+)-\d+-[^-]+$")[0]
sample["idx"] = sample["class_id"].str.split("_").str[0]

record = json.loads(get(f"https://zenodo.org/api/records/{RECORD}"))
zfile = record["files"][0]
print(f"Zenodo {RECORD} {record['metadata'].get('version')}: {zfile['key']} ({zfile['checksum']})")
zf = zipfile.ZipFile(HttpRangeFile(zfile["links"]["self"], zfile["size"]))
names = zf.namelist()

wanted = []
for project, group in sample.groupby("project"):
    base = f"Data/change_proneness_data/{project}/"
    wanted += [base + f for f in PROJECT_FILES]
    prefixes = tuple(f"{base}class_change_history/{idx}_" for idx in group["idx"].unique())
    wanted += [n for n in names if n.startswith(prefixes) and not n.endswith("/")]

manifest = []
for name in wanted:
    target = OUT / name
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zf.read(name))  
    data = target.read_bytes()
    manifest.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    print(f"  {name} ({len(data)} bytes)")

pd.DataFrame(manifest).to_csv("M2/inputs/zenodo_manifest.csv", index=False)
print(f"Extracted {len(manifest)} files to {OUT}")
