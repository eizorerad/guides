"""Small synthetic examples for the coordinate conventions used in the report."""

import unittest

from guides.analysis import find_matches, overlap_bp, reverse_complement
from guides.data import validate_guides


class Coordinates(unittest.TestCase):
    spacer = "AGTCCGATGCTAACGTCGTA"

    def test_plus_strand_and_genomic_offset(self):
        result = find_matches("TTT" + self.spacer + "TGG", self.spacer, offset=100)
        self.assertEqual(result, [dict(start=103, end=123, strand="+", pam="TGG")])

    def test_minus_strand_pam_is_upstream_on_reference(self):
        sequence = "AAA" + "CCG" + reverse_complement(self.spacer) + "TTT"
        result = find_matches(sequence, self.spacer, offset=100)
        self.assertEqual(result, [dict(start=106, end=126, strand="-", pam="CGG")])

    def test_sequence_without_valid_pam_is_not_a_placement(self):
        self.assertEqual(find_matches(self.spacer + "TGA", self.spacer), [])
        self.assertEqual(find_matches(self.spacer + "NGG", self.spacer), [])

    def test_multiple_exact_placements_are_kept(self):
        sequence = self.spacer + "TGGTTT" + self.spacer + "AGG"
        self.assertEqual([m["start"] for m in find_matches(sequence, self.spacer)], [0, 26])

    def test_overlapping_peaks_do_not_double_count_bases(self):
        self.assertEqual(overlap_bp([(5, 15), (10, 20)], 0, 23), 15)
        self.assertEqual(overlap_bp([(0, 10), (20, 30)], 10, 20), 0)

    def test_pam_is_not_accepted_as_part_of_user_spacer(self):
        with self.assertRaises(ValueError):
            validate_guides([self.spacer + "TGG"])
        self.assertEqual(validate_guides([self.spacer.lower()]), [self.spacer])


if __name__ == "__main__":
    unittest.main()
