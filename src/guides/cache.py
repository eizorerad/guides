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


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(dir=path.parent) as tmp:
        new = Path(tmp) / path.name
        new.write_bytes(data)
        new.chmod(0o444)
        new.replace(path)


def query_path(url, body=None):
    return RAW / "regions" / (sha256(canonical([url, body])) + ".json")


def require_ok(response, *args, **kwargs):
    # Run before Requests can follow a redirect or read its body.
    if response.status_code != 200:
        response.close()
        raise ValueError(f"HTTP {response.status_code}: {response.url}")


def response_data(reply, field, params, url):
    if field is None:
        return reply  # JBrowse chunks are lists.
    if not isinstance(reply, dict):
        raise ValueError(f"Expected a JSON object from {url}")
    coordinates = ("genome", "chrom", "start", "end", "track") if "genome" in params else ()
    if any(reply.get(k) != params[k] for k in coordinates if k in params):
        raise ValueError(f"Unexpected coordinates or track in response from {url}")
    data = reply.get(field, [] if field == "positionMatches" else None)
    if data is None:
        raise ValueError(f"Missing {field} in response from {url}")
    if field == "dna" and (not isinstance(data, str) or len(data) != params["end"] - params["start"]):
        raise ValueError(f"Incomplete GRCh38 sequence from {url}")
    return data


class Inputs:
    def __init__(self, limit=None, used=0):
        self.limit = limit
        self.used = used
        self.sources = {}

    def fetch(self, url, limit, body=None):
        if self.limit is not None:
            limit = min(limit, self.limit - self.used)
        too_large = f"Download exceeds the {limit:,}-byte limit: {url}"
        if limit <= 0:
            raise ValueError(too_large)
        headers = {"Accept": "application/json, */*", "Accept-Encoding": "identity"}
        method = "GET" if body is None else "POST"
        with requests.request(method, url, json=body, headers=headers, stream=True, timeout=45,
                              allow_redirects=False, hooks={"response": require_ok}) as response:
            size = int(response.headers.get("Content-Length", -1))
            if size > limit:
                raise ValueError(too_large)
            encoding = response.headers.get("Content-Encoding", "identity").lower()
            if encoding not in {"identity", "gzip", "x-gzip"}:
                raise ValueError(f"Unexpected HTTP encoding {encoding!r}: {url}")
            try:
                wire = response.raw.read(limit, decode_content=False)
                data = wire if encoding == "identity" else gzip.GzipFile(fileobj=BytesIO(wire)).read(limit + 1)
            except (HTTPError, EOFError, OSError, zlib.error) as error:
                raise ValueError(f"Invalid {encoding} response: {url}") from error
            if size >= 0 and len(wire) != size:
                raise ValueError(f"Incomplete download: {url}")
            if len(data) > limit or (size < 0 and len(wire) == limit and not response.raw.isclosed()):
                raise ValueError(too_large)
            self.used += max(len(wire), len(data))
            return data

    def file(self, key, source):
        path = RAW / source["filename"]
        cached = path.is_file()
        if cached:
            with path.open("rb") as stream:
                data = stream.read(source["bytes"] + 1)
        else:
            data = self.fetch(source["url"], source["bytes"] + 1)
        if hashlib.md5(data).hexdigest() != source["md5"]:
            raise ValueError(f"Checksum mismatch: {path}. Remove it and retry.")
        if not cached:
            save(path, data)
        self.sources[path] = dict(source, key=key, sha256=sha256(data))
        return path

    def json(self, key, source, url, field, limit, params, body=None):
        path = query_path(url, body)
        cached = path.is_file()
        if cached:
            record = json.loads(path.read_bytes())
            data = record.get("data") if isinstance(record, dict) else None
        else:
            data = response_data(json.loads(self.fetch(url, limit, body)), field, params, url)
        digest = sha256(canonical(data))
        expected = dict(url=url, body=body, sha256=digest)
        if not cached:
            save(path, canonical(dict(expected, data=data)))
        elif not isinstance(record, dict) or any(record.get(k) != v for k, v in expected.items()):
            raise ValueError(f"Cached response checksum mismatch: {path}. Remove it and retry.")
        self.sources[path] = dict(source, key=key, url=url, query=params,
                                  filename=str(path.relative_to(RAW)), sha256=digest)
        return data
