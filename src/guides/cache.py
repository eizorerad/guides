"""Bounded downloads and a checked, read-only cache."""

import gzip
import hashlib
import json
import zlib
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory

import requests
from urllib3.exceptions import HTTPError

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw"


def canonical(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":")).encode()


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def checksum(path, algorithm="sha256"):
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, algorithm).hexdigest()


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=path.parent) as tmp:
        new = Path(tmp) / path.name
        new.write_bytes(data)
        new.chmod(0o444)
        new.replace(path)


def query_path(url, body=None):
    return RAW / "regions" / (sha256(canonical([url, body])) + ".json")


def direct_response(response, *args, **kwargs):
    # Requests would otherwise read a redirect body before we can apply the byte limit.
    if 300 <= response.status_code < 400:
        response.close()
        raise ValueError(f"Unexpected redirect: {response.url}")


class Inputs:
    def __init__(self, limit=None, used=0):
        self.limit = limit
        self.used = used
        self.sources = {}

    def fetch(self, url, limit, body=None):
        if self.limit is not None:
            limit = min(limit, self.limit - self.used)
        headers = {"Accept": "application/json, */*", "Accept-Encoding": "identity"}
        method = "POST" if body else "GET"
        with requests.request(method, url, json=body, headers=headers, stream=True, timeout=45,
                              allow_redirects=False, hooks={"response": direct_response}) as response:
            response.raise_for_status()
            if response.status_code == 206:
                raise ValueError(f"Incomplete response from {url}")
            size = response.headers.get("Content-Length")
            too_large = f"Download exceeds the {limit:,}-byte limit: {url}"
            if limit <= 0 or (size is not None and int(size) > limit):
                raise ValueError(too_large)
            # Bound the actual HTTP body, including replies without Content-Length.
            try:
                wire = response.raw.read(limit, decode_content=False)
            except HTTPError as error:
                raise ValueError(f"Interrupted download: {url}") from error
            if size is not None and len(wire) != int(size):
                raise ValueError(f"Incomplete download: {url}")
            if size is None and len(wire) == limit and not response.raw.isclosed():
                raise ValueError(too_large)
            data = wire
            encoding = response.headers.get("Content-Encoding", "identity").lower()
            if encoding in {"gzip", "x-gzip"}:
                try:
                    with gzip.GzipFile(fileobj=BytesIO(wire)) as stream:
                        data = stream.read(limit + 1)
                except (EOFError, OSError, zlib.error) as error:
                    raise ValueError(f"Invalid gzip response: {url}") from error
            elif encoding != "identity":
                raise ValueError(f"Unexpected HTTP encoding {encoding!r}: {url}")
            if len(data) > limit:
                raise ValueError(too_large)
            self.used += max(len(wire), len(data))
            return data

    def file(self, key, source):
        path = RAW / source["filename"]
        if not path.exists():
            print(f"Downloading {path.name} …", flush=True)
            data = self.fetch(source["url"], source["bytes"] + 1)
            if hashlib.md5(data).hexdigest() != source["md5"]:
                raise ValueError(f"Download checksum mismatch: {path.name}")
            save(path, data)
        if checksum(path, "md5") != source["md5"]:
            raise ValueError(f"Changed raw file: {path}. Remove it and download again.")
        self.sources[path] = dict(source, key=key, sha256=checksum(path))
        return path

    def json(self, key, source, url, field, limit, params, body=None):
        path = query_path(url, body)
        if path.exists():
            record = json.loads(path.read_bytes())
            data = record.get("data")
            valid_query = record.get("url") == url and record.get("body") == body
            if not valid_query or record.get("sha256") != sha256(canonical(data)):
                raise ValueError(f"Cached response checksum mismatch: {path}. Remove it and retry.")
        else:
            reply = json.loads(self.fetch(url, limit, body))
            if "genome" in params:  # Check that UCSC answered for the requested assembly and interval.
                if any(reply.get(k) != v for k, v in params.items() if k in {"genome", "chrom", "start", "end", "track"}):
                    raise ValueError(f"Unexpected coordinates or track in response from {url}")
                if field == "positionMatches":
                    reply.setdefault(field, [])
            if field is not None and field not in reply:
                raise ValueError(f"Missing {field} in response from {url}")
            data = reply if field is None else reply[field]
            if field == "dna" and len(data) != params["end"] - params["start"]:
                raise ValueError(f"Incomplete GRCh38 sequence from {url}")
            record = dict(url=url, body=body, data=data, sha256=sha256(canonical(data)))
            save(path, canonical(record))
        self.sources[path] = dict(source, key=key, url=url, query=params,
                                  filename=str(path.relative_to(RAW)), sha256=record["sha256"])
        return data
