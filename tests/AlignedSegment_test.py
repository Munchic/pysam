import os
import pysam
import unittest
from TestUtils import checkFieldEqual

SAMTOOLS = "samtools"
WORKDIR = "pysam_test_work"
DATADIR = "pysam_data"


class ReadTest(unittest.TestCase):
    pass


class TestAlignedSegment(ReadTest):

    '''tests to check if aligned read can be constructed
    and manipulated.
    '''

    def testEmpty(self):
        a = pysam.AlignedSegment()
        self.assertEqual(a.query_name, None)
        self.assertEqual(a.query_sequence, None)
        self.assertEqual(pysam.toQualityString(a.query_qualities), None)
        self.assertEqual(a.flag, 0)
        self.assertEqual(a.reference_id, 0)
        self.assertEqual(a.mapping_quality, 0)
        self.assertEqual(a.cigartuples, None)
        self.assertEqual(a.tags, [])
        self.assertEqual(a.next_reference_id, 0)
        self.assertEqual(a.next_reference_start, 0)
        self.assertEqual(a.template_length, 0)

    def testStrOfEmptyRead(self):
        a = pysam.AlignedSegment()
        s = str(a)
        self.assertEqual(
            "None\t0\t0\t0\t0\tNone\t0\t0\t0\tNone\tNone\t[]",
            s)

    def buildRead(self):
        '''build an example read.'''

        a = pysam.AlignedSegment()
        a.query_name = "read_12345"
        a.query_sequence = "ACGT" * 10
        a.flag = 0
        a.reference_id = 0
        a.reference_start = 20
        a.mapping_quality = 20
        a.cigartuples = ((0, 10), (2, 1), (0, 9), (1, 1), (0, 20))
        a.next_reference_id = 0
        a.next_reference_start = 200
        a.template_length = 167
        a.query_qualities = pysam.fromQualityString("1234") * 10
        # todo: create tags
        return a

    def testSettingTagInEmptyRead(self):
        '''see issue 62'''
        a = pysam.AlignedSegment()
        a.tags = (("NM", 1),)
        a.query_qualities = None
        self.assertEqual(a.tags, [("NM", 1), ])

    def testUpdate(self):
        '''check if updating fields affects other variable length data
        '''
        a = self.buildRead()
        b = self.buildRead()

        # check qname
        b.query_name = "read_123"
        checkFieldEqual(self, a, b, "query_name")
        b.query_name = "read_12345678"
        checkFieldEqual(self, a, b, "query_name")
        b.query_name = "read_12345"
        checkFieldEqual(self, a, b)

        # check cigar
        b.cigartuples = ((0, 10), )
        checkFieldEqual(self, a, b, "cigartuples")
        b.cigartuples = ((0, 10), (2, 1), (0, 10))
        checkFieldEqual(self, a, b, "cigartuples")
        b.cigartuples = ((0, 10), (2, 1), (0, 9), (1, 1), (0, 20))
        checkFieldEqual(self, a, b)

        # check seq
        b.query_sequence = "ACGT"
        checkFieldEqual(self, 
            a, b,
            ("query_sequence", "query_qualities", "query_length"))
        b.query_sequence = "ACGT" * 3
        checkFieldEqual(self, 
            a, b,
            ("query_sequence", "query_qualities", "query_length"))
        b.query_sequence = "ACGT" * 10
        checkFieldEqual(self, a, b, ("query_qualities",))

        # reset qual
        b = self.buildRead()

        # check flags:
        for x in (
                "is_paired", "is_proper_pair",
                "is_unmapped", "mate_is_unmapped",
                "is_reverse", "mate_is_reverse",
                "is_read1", "is_read2",
                "is_secondary", "is_qcfail",
                "is_duplicate"):
            setattr(b, x, True)
            self.assertEqual(getattr(b, x), True)
            checkFieldEqual(self, a, b, ("flag", x,))
            setattr(b, x, False)
            self.assertEqual(getattr(b, x), False)
            checkFieldEqual(self, a, b)

    def testUpdate2(self):
        '''issue 135: inplace update of sequence and quality score.

        This does not work as setting the sequence will erase
        the quality scores.
        '''
        a = self.buildRead()
        a.query_sequence = a.query_sequence[5:10]
        self.assertEqual(pysam.toQualityString(a.query_qualities), None)

        a = self.buildRead()
        s = pysam.toQualityString(a.query_qualities)
        a.query_sequence = a.query_sequence[5:10]
        a.query_qualities = pysam.fromQualityString(s[5:10])

        self.assertEqual(pysam.toQualityString(a.query_qualities), s[5:10])

    def testLargeRead(self):
        '''build an example read.'''

        a = pysam.AlignedSegment()
        a.query_name = "read_12345"
        a.query_sequence = "ACGT" * 200
        a.flag = 0
        a.reference_id = 0
        a.reference_start = 20
        a.mapping_quality = 20
        a.cigartuples = ((0, 4 * 200), )
        a.next_reference_id = 0
        a.next_reference_start = 200
        a.template_length = 167
        a.query_qualities = pysam.fromQualityString("1234") * 200

        return a

    def testTagParsing(self):
        '''test for tag parsing

        see http://groups.google.com/group/pysam-user-group/browse_thread/thread/67ca204059ea465a
        '''
        samfile = pysam.AlignmentFile(os.path.join(DATADIR, "ex8.bam"),
                                "rb")

        for entry in samfile:
            before = entry.tags
            entry.tags = entry.tags
            after = entry.tags
            self.assertEqual(after, before)

    def testUpdateTlen(self):
        '''check if updating tlen works'''
        a = self.buildRead()
        oldlen = a.template_length
        oldlen *= 2
        a.template_length = oldlen
        self.assertEqual(a.template_length, oldlen)

    def testPositions(self):
        a = self.buildRead()
        self.assertEqual(a.get_reference_positions(),
                         [20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
                          31, 32, 33, 34, 35, 36, 37, 38, 39,
                          40, 41, 42, 43, 44, 45, 46, 47, 48, 49,
                          50, 51, 52, 53, 54, 55, 56, 57, 58, 59])

        self.assertEqual(a.get_aligned_pairs(),
                         [(0, 20), (1, 21), (2, 22), (3, 23), (4, 24),
                          (5, 25), (6, 26), (7, 27), (8, 28), (9, 29),
                          (None, 30),
                          (10, 31), (11, 32), (12, 33), (13, 34), (14, 35),
                          (15, 36), (16, 37), (17, 38), (18, 39), (19, None),
                          (20, 40), (21, 41), (22, 42), (23, 43), (24, 44),
                          (25, 45), (26, 46), (27, 47), (28, 48), (29, 49),
                          (30, 50), (31, 51), (32, 52), (33, 53), (34, 54),
                          (35, 55), (36, 56), (37, 57), (38, 58), (39, 59)])

        self.assertEqual(
            a.get_reference_positions(),
            [x[1] for x in a.get_aligned_pairs()
             if x[0] is not None and x[1] is not None])
        # alen is the length of the aligned read in genome
        self.assertEqual(a.reference_length,
                         a.get_aligned_pairs()[-1][0] + 1)
        # aend points to one beyond last aligned base in ref
        self.assertEqual(a.get_reference_positions()[-1],
                         a.reference_end - 1)

    def testFullReferencePositions(self):
        '''see issue 26'''
        a = self.buildRead()
        a.cigar = [(4, 30), (0, 20), (1, 3), (0, 47)]

        self.assertEqual(100,
                         len(a.get_reference_positions(full_length=True)))

    def testBlocks(self):
        a = self.buildRead()
        self.assertEqual(a.get_blocks(),
                         [(20, 30), (31, 40), (40, 60)])

    # Disabled as not backwards compatible
    # def testFancyStr(self):
    #     a = self.buildRead()
    #     output = a.fancy_str()
    #     self.assertEqual(len(output), 9)

    def testAddTagsType(self):
        a = self.buildRead()
        a.tags = None
        self.assertEqual(a.tags, [])

        a.setTag('X1', 5.0)
        a.setTag('X2', "5.0")
        a.setTag('X3', 5)

        self.assertEqual(sorted(a.tags),
                         sorted([('X1', 5.0),
                                 ('X2', "5.0"),
                                 ('X3', 5)]))

        # test setting float for int value
        a.setTag('X4', 5, value_type='d')
        self.assertEqual(sorted(a.tags),
                         sorted([('X1', 5.0),
                                 ('X2', "5.0"),
                                 ('X3', 5),
                                 ('X4', 5.0)]))

        # test setting int for float value - the
        # value will be rounded.
        a.setTag('X5', 5.2, value_type='i')
        self.assertEqual(sorted(a.tags),
                         sorted([('X1', 5.0),
                                 ('X2', "5.0"),
                                 ('X3', 5),
                                 ('X4', 5.0),
                                 ('X5', 5)]))

        # test setting invalid type code
        self.assertRaises(ValueError, a.setTag, 'X6', 5.2, 'g')

    def testTagsUpdatingFloat(self):
        a = self.buildRead()
        a.tags = [('NM', 1), ('RG', 'L1'),
                  ('PG', 'P1'), ('XT', 'U')]
 
        self.assertEqual(a.tags,
                         [('NM', 1), ('RG', 'L1'),
                          ('PG', 'P1'), ('XT', 'U')])
        a.tags += [('XC', 5.0)]
        self.assertEqual(a.tags,
                         [('NM', 1), ('RG', 'L1'),
                          ('PG', 'P1'), ('XT', 'U'), ('XC', 5.0)])

    def testAddTags(self):
        a = self.buildRead()
        a.tags = [('NM', 1), ('RG', 'L1'),
                  ('PG', 'P1'), ('XT', 'U')]

        self.assertEqual(sorted(a.tags),
                         sorted([('NM', 1), ('RG', 'L1'),
                                 ('PG', 'P1'), ('XT', 'U')]))

        a.setTag('X1', 'C')
        self.assertEqual(sorted(a.tags),
                         sorted([('X1', 'C'), ('NM', 1), ('RG', 'L1'),
                                 ('PG', 'P1'), ('XT', 'U'), ]))
        a.setTag('X2', 5)
        self.assertEqual(sorted(a.tags),
                         sorted([('X2', 5), ('X1', 'C'),
                                 ('NM', 1), ('RG', 'L1'),
                                 ('PG', 'P1'), ('XT', 'U'), ]))
        # add with replacement
        a.setTag('X2', 10)
        self.assertEqual(sorted(a.tags),
                         sorted([('X2', 10), ('X1', 'C'),
                                 ('NM', 1), ('RG', 'L1'),
                                 ('PG', 'P1'), ('XT', 'U'), ]))

        # add without replacement
        a.setTag('X2', 5, replace=False)
        self.assertEqual(sorted(a.tags),
                         sorted([('X2', 10), ('X1', 'C'),
                                 ('X2', 5),
                                 ('NM', 1), ('RG', 'L1'),
                                 ('PG', 'P1'), ('XT', 'U'), ]))

    def testMissingOpt(self):
        a = self.buildRead()
        self.assertRaises(KeyError, a.opt, "XP")

    def testEmptyOpt(self):
        a = self.buildRead()
        self.assertRaises(KeyError, a.opt, "XT")


if __name__ == "__main__":
    unittest.main()
