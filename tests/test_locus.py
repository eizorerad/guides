"""Offline checks of the regional data path."""

import gzip
import json
from io import BytesIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from guides import cache
from guides.cache import Inputs
from guides.locus import annotation, gene_anchor, read_context


class Locus(unittest.TestCase):
    def test_lookup_rejects_ambiguous_primary_loci(self):
        hit = dict(posName="ENSG00000000001.3", position="chr7:11-20")
        group = {"matches": [hit, dict(hit, posName="ENSG00000000010.1", position="chr1:4-8")]}
        self.assertEqual(gene_anchor([group], "ENSG00000000001"), ("ENSG00000000001.3", "chr7", 10))
        group["matches"].append(dict(hit, position="chrX:11-20"))
        with self.assertRaisesRegex(ValueError, "locus"):
            gene_anchor([group], "ENSG00000000001")

    def test_nested_genes_and_basic_tss_on_both_strands(self):
        names = [["Start", "End", "Chunk"], ["Start", "End", "Strand", "Type", "Gene_name", "Gene_id", "Subfeatures"],
                 ["Start", "End", "Type", "Tag"]]
        index = dict(classes=[{"attributes": n} for n in names], lazyClass=0,
                     nclist=[[0, 0, 50, 1]], urlTemplate="lf-{Chunk}.jsonz")
        nested = [1, 10, 25, 1, "gene", "B", "idB", [[2, 12, 25, "transcript", ["basic", "other"]]]]
        outer = [1, 0, 50, -1, "gene", "A", "idA",
                 [[2, 0, 48, "transcript", "basic"], [2, 0, 49, "transcript", "other"]],
                 {"Sublist": [nested]}]
        inputs = Mock()
        inputs.json.side_effect = [index, [outer]]
        self.assertEqual([(g["gene"], t) for g, t in annotation(inputs, "chr7", 16, 17)],
                         [("A", [47]), ("B", [12])])

    def test_empty_interval_keeps_csv_columns(self):
        with patch("guides.locus.annotation", return_value=[]), patch("guides.locus.ucsc", return_value=[]):
            genes, ccres = read_context("chr1", (1, 2), (0, 20), Inputs())
        self.assertTrue(genes.empty and ccres.empty)
        self.assertEqual(list(ccres), ["chrom", "start", "end", "accession", "cCRE_class"])

    def test_cache_checks_hash_and_reuses_the_response(self):
        url = "https://example.org/region"
        with tempfile.TemporaryDirectory() as directory, patch.object(cache, "RAW", Path(directory)):
            inputs = Inputs()
            args = ("test", {}, url, "dna", 100, {"start": 0, "end": 4})
            with patch.object(inputs, "fetch", return_value=b'{"dna":"ACGT"}') as get:
                self.assertEqual(inputs.json(*args), "ACGT")
                self.assertEqual(inputs.json(*args), "ACGT")
                get.assert_called_once()
            path = cache.query_path(url)
            record = json.loads(path.read_bytes())
            path.chmod(0o644)
            del record["body"]  # Older GET records can omit the body.
            record["note"] = "local metadata"
            path.write_text(json.dumps(record))
            self.assertEqual(Inputs(limit=0).json(*args), "ACGT")
            record["data"] = "AAAA"
            path.write_text(json.dumps(record))
            with self.assertRaisesRegex(ValueError, "checksum"):
                inputs.json(*args)

    def test_redirect_is_closed_before_its_body_is_read(self):
        response = Mock(status_code=302, url="https://example.org/redirect")
        with self.assertRaisesRegex(ValueError, "HTTP 302"):
            cache.require_ok(response)
        response.close.assert_called_once()
        response.raw.read.assert_not_called()

    def test_truncated_gzip_never_enters_the_cache(self):
        data = gzip.compress(b"[]")[:-3]
        response = Mock(headers={"Content-Encoding": "gzip", "Content-Length": str(len(data))})
        response.raw.read.return_value = data
        with tempfile.TemporaryDirectory() as directory, patch.object(cache, "RAW", Path(directory)):
            with patch.object(cache.requests, "request") as get:
                get.return_value.__enter__.return_value = response
                with self.assertRaisesRegex(ValueError, "gzip"):
                    Inputs().json("test", {}, "https://example.org/data", None, 100, {})
            self.assertFalse(list(Path(directory).iterdir()))

    def test_budget_stops_a_stream_without_content_length(self):
        response = Mock(headers={})
        stream = BytesIO(b"123456789")
        response.raw.read.side_effect = lambda size, **_: stream.read(size)
        response.raw.isclosed.return_value = False
        with patch.object(cache.requests, "request") as get:
            get.return_value.__enter__.return_value = response
            with self.assertRaisesRegex(ValueError, "limit"):
                Inputs(limit=10, used=6).fetch("https://example.org/region", 100)
        self.assertEqual(stream.tell(), 4)

    def test_exhausted_budget_opens_no_connection(self):
        with patch.object(cache.requests, "request") as get:
            with self.assertRaisesRegex(ValueError, "limit"):
                Inputs(limit=8_000_000, used=8_000_000).fetch("https://example.org/region", 100)
            get.assert_not_called()
