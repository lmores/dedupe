import unittest

from future.builtins import str

from dedupe import _predicates as fn
from dedupe.cpredicates import ngrams


class TestPredicateFunctions(unittest.TestCase):
    def testWholeFieldPredicate(self):
        self.assertEqual(fn.wholeFieldPredicate('donald'), ('donald',))
        self.assertEqual(fn.wholeFieldPredicate('go-of,y  '), ('go-of,y  ',))
        self.assertEqual(fn.wholeFieldPredicate(' cip ciop '), (' cip ciop ',))

    def testTokenFieldPredicate(self):
        self.assertEqual(fn.tokenFieldPredicate('donald'), set(('donald',)))
        self.assertEqual(fn.tokenFieldPredicate('do\nal d'), set(('do', 'al', 'd')))
        self.assertEqual(fn.tokenFieldPredicate('go-of y  '), set(('go', 'of', 'y')))
        self.assertEqual(fn.tokenFieldPredicate(' cip\n\n\nciop '), set(('cip', 'ciop')))

    def testFirstTokenPredicate(self):
        self.assertEqual(fn.firstTokenPredicate('donald'), ('donald',))
        self.assertEqual(fn.firstTokenPredicate('don ald'), ('don',))
        self.assertEqual(fn.firstTokenPredicate('do\nal d'), ('do',))
        self.assertEqual(fn.firstTokenPredicate('go-of y  '), ('go',))
        self.assertEqual(fn.firstTokenPredicate(' cip\n\n\nciop '), ())

    def testTwoTokensPredicate(self):
        self.assertEqual(fn.firstTwoTokensPredicate('donald'), ())
        self.assertEqual(fn.firstTwoTokensPredicate('don ald'), ('don ald',))
        self.assertEqual(fn.firstTwoTokensPredicate('do\nal d'), ('do\nal',))
        self.assertEqual(fn.firstTwoTokensPredicate('go-of y  '), ('go-of',))
        self.assertEqual(fn.firstTwoTokensPredicate(' cip\n\n\nciop '), ())

    def testCommonIntegerPredicate(self):
        self.assertEqual(fn.commonIntegerPredicate('don4ld'), set(('4',)))
        self.assertEqual(fn.commonIntegerPredicate('donald 1992'), set(('1992',)))
        self.assertEqual(fn.commonIntegerPredicate('g00fy  '), set(('0',)))  # !!!
        self.assertEqual(fn.commonIntegerPredicate(' c1p\n\n\nc10p '), set(('1', '10')))

    def testAlphaNumericPredicate(self):
        self.assertEqual(fn.alphaNumericPredicate('don4ld'), set(('don4ld',)))
        self.assertEqual(fn.alphaNumericPredicate('donald 1992'), set())
        self.assertEqual(fn.alphaNumericPredicate('g00fy  '), set(('g00fy',)))
        self.assertEqual(fn.alphaNumericPredicate(' c1p\n\n\nc10p '), set(('c1p', 'c10p')))

    def testNearIntegersPredicate(self):
        self.assertEqual(fn.nearIntegersPredicate('don4ld'), set(('3', '4', '5')))
        self.assertEqual(fn.nearIntegersPredicate('donald 1992'), set(('1991', '1992', '1993')))
        self.assertEqual(fn.nearIntegersPredicate('g00fy  '), set(('-1', '0', '1')))
        self.assertEqual(fn.nearIntegersPredicate(' c1p\n\n\nc10p '), set(('0', '1', '2', '9', '10', '11')))

    def testHundredIntegersPredicate(self):
        self.assertEqual(fn.hundredIntegerPredicate('don456ld'), set(('400',)))
        self.assertEqual(fn.hundredIntegerPredicate('donald 1992'), set(('1900',)))
        self.assertEqual(fn.hundredIntegerPredicate('g00fy  '), set(('00', )))
        self.assertEqual(fn.hundredIntegerPredicate(' c111p\n\n\nc1230p '), set(('100', '1200')))

    def testHundredIntegersOddPredicate(self):
        self.assertEqual(fn.hundredIntegersOddPredicate('don456ld'), set(('400',)))
        self.assertEqual(fn.hundredIntegersOddPredicate('donald 1991'), set(('1901',)))
        self.assertEqual(fn.hundredIntegersOddPredicate('g00fy  '), set(('00', )))
        self.assertEqual(fn.hundredIntegersOddPredicate(' c111p\n\n\nc1230p '), set(('101', '1200')))

    def testFirstIntegerPredicate(self):
        self.assertEqual(fn.firstIntegerPredicate('donald 456'), ())
        self.assertEqual(fn.firstIntegerPredicate('1992 donald'), ('1992',))
        self.assertEqual(fn.firstIntegerPredicate('00fy  '), ('00',))  # !!!
        self.assertEqual(fn.firstIntegerPredicate('111 p\n\n\nc1230p '), ('111',))

    def testCommonTwoTokens(self):
        self.assertEqual(fn.commonTwoTokens('d on 456 ld'), set(('d on', 'on 456', '456 ld')))
        self.assertEqual(fn.commonTwoTokens('donald 1992'), set(('donald 1992',)))
        self.assertEqual(fn.commonTwoTokens('g00fy  '), set())
        self.assertEqual(fn.commonTwoTokens(' c1p\n\n\nc10p '), set(('c1p c10p',)))

    def testCommonThreeTokens(self):
        self.assertEqual(fn.commonThreeTokens('d on 456 ld'), set(('d on 456', 'on 456 ld')))
        self.assertEqual(fn.commonThreeTokens('donald 1992'), set(()))
        self.assertEqual(fn.commonThreeTokens('g00fy  '), set())
        self.assertEqual(fn.commonThreeTokens(' c1p\n\n\nc10p  c100p'), set(('c1p c10p c100p',)))

    def testFingerprint(self):
        self.assertEqual(fn.fingerprint('don 456 ld '), ('456donld',))
        self.assertEqual(fn.fingerprint('donald 1991'), ('1991donald',))
        self.assertEqual(fn.fingerprint(' g00fy  '), ('g00fy', ))
        self.assertEqual(fn.fingerprint(' c11p\n\n\nc10p '), ('c10pc11p',))

    def testOneGramFingerprint(self):
        def prevImpl(field: str):
            return ("".join(sorted(set(ngrams(field.replace(" ", ""), 1)))).strip(),)

        self.assertEqual(fn.oneGramFingerprint('don 456 ld'), ('456dlno',))
        self.assertEqual(fn.oneGramFingerprint('donald 1992'), ('129adlno',))
        self.assertEqual(fn.oneGramFingerprint(' g00fy  '), ('0fgy', ))
        self.assertEqual(fn.oneGramFingerprint(' c1p\n\n\nc10p '), ('01cp',))

        self.assertEqual(fn.oneGramFingerprint('don 456 ld'), prevImpl('don 456 ld'))
        self.assertEqual(fn.oneGramFingerprint('donald 1992'), prevImpl('donald 1992'))
        self.assertEqual(fn.oneGramFingerprint(' g00fy  '), prevImpl(' g00fy  '))
        self.assertEqual(fn.oneGramFingerprint(' c1p\n\n\nc10p '), prevImpl(' c1p\n\n\nc10p '))

    def testTwoGramFingerprint(self):
        def prevImpl(field: str):
            if len(field) > 1:
                return (
                    "".join(
                        sorted(gram.strip() for gram in set(ngrams(field.replace(" ", ""), 2)))
                    ),
                )
            else:
                return ()

        self.assertEqual(fn.twoGramFingerprint('don4ld'), ('4ldoldn4on',))
        self.assertEqual(fn.twoGramFingerprint('donald 1992'), ('199299ald1doldnaon',))
        self.assertEqual(fn.twoGramFingerprint('g00fy  '), ('000ffyg0', ))
        self.assertEqual(fn.twoGramFingerprint(' c1p\n\n\nc10p '), ('0p101pc1pc',))
        self.assertEqual(fn.twoGramFingerprint('7'), ())

        self.assertEqual(fn.twoGramFingerprint('don4ld'), prevImpl('don4ld'))
        self.assertEqual(fn.twoGramFingerprint('donald 1992'), prevImpl('donald 1992'))
        self.assertEqual(fn.twoGramFingerprint('g00fy'), prevImpl('g00fy'))
        #self.assertEqual(fn.twoGramFingerprint(' c1p\n\n\nc10p '), prevImpl(' c1p\n\n\nc10p '))
        self.assertEqual(fn.twoGramFingerprint('a'), prevImpl('a'))

    def testCommonFourGram(self):
        self.assertEqual(fn.commonFourGram('don4ld'), set(('don4', 'on4l', 'n4ld')))
        self.assertEqual(fn.commonFourGram('donald 1992'), set(('dona', 'onal', 'nald', 'ald1', 'ld19', 'd199', '1992')))
        self.assertEqual(fn.commonFourGram('g00fy  '), set(('g00f', '00fy')))
        self.assertEqual(fn.commonFourGram(' c1p\n\n\nc10p '), set(('c1pc', '1pc1', 'pc10', 'c10p')))

    def testCommonSixGram(self):
        self.assertEqual(fn.commonSixGram('don4ld'), set(('don4ld',)))
        self.assertEqual(fn.commonSixGram('donald 1992'), set(('donald', 'onald1', 'nald19', 'ald199', 'ld1992')))
        self.assertEqual(fn.commonSixGram('g00fy  '), set())
        self.assertEqual(fn.commonSixGram(' c1p\n\n\nc10p '), set(('c1pc10', '1pc10p')))

    def testSameThreeCharStartPredicate(self):
        self.assertEqual(fn.sameThreeCharStartPredicate('don4ld'), ('don',))
        self.assertEqual(fn.sameThreeCharStartPredicate('donald 1992'), ('don',))
        self.assertEqual(fn.sameThreeCharStartPredicate('g00fy  '), ('g00',))
        self.assertEqual(fn.sameThreeCharStartPredicate(' c1p\n\n\nc10p '), ('c1p',))

    def testSameFiveCharStartPredicate(self):
        self.assertEqual(fn.sameFiveCharStartPredicate('don4ld'), ('don4l',))
        self.assertEqual(fn.sameFiveCharStartPredicate('donald 1992'), ('donal',))
        self.assertEqual(fn.sameFiveCharStartPredicate('g00fy  '), ('g00fy',))
        self.assertEqual(fn.sameFiveCharStartPredicate(' c1p\n\n\nc10p '), ('c1pc1',))

    def testSameSevenCharStartPredicate(self):
        self.assertEqual(fn.sameSevenCharStartPredicate('don4ld'), ('don4ld',))
        self.assertEqual(fn.sameSevenCharStartPredicate('donald 1992'), ('donald1',))
        self.assertEqual(fn.sameSevenCharStartPredicate('g00fy  '), ('g00fy',))
        self.assertEqual(fn.sameSevenCharStartPredicate(' c1p\n\n\nc10p '), ('c1pc10p',))

    def testSuffixArray(self):
        self.assertEqual(tuple(fn.suffixArray('don4ld')), ('don4ld', 'on4ld'))
        self.assertEqual(tuple(fn.suffixArray('donald 1992')), ('donald 1992', 'onald 1992', 'nald 1992', 'ald 1992', 'ld 1992', 'd 1992', ' 1992'))
        self.assertEqual(tuple(fn.suffixArray('g00fy  ')), ('g00fy  ', '00fy  ', '0fy  '))
        self.assertEqual(tuple(fn.suffixArray(' c1p\nc10p ')), (' c1p\nc10p ', 'c1p\nc10p ', '1p\nc10p ', 'p\nc10p ', '\nc10p ', 'c10p '))

    def testSortedAcronym(self):
        self.assertEqual(fn.sortedAcronym('don 4l d'), ('4dd',))
        self.assertEqual(fn.sortedAcronym('donald 19 92'), ('19d',))
        self.assertEqual(fn.sortedAcronym('g 00f y  '), ('0gy',))
        self.assertEqual(fn.sortedAcronym(' c1p\n\n\nc10p '), ('cc',))

    def testDoubleMetaphone(self):
        self.assertEqual(fn.doubleMetaphone('i'), set(('A',)))
        self.assertEqual(fn.doubleMetaphone('donald'), set(('TNLT',)))
        self.assertEqual(fn.doubleMetaphone('goofy'), set(('KF',)))
        self.assertEqual(fn.doubleMetaphone('cipciop'), set(('SPSP', 'SPXP')))

    def testMetaphoneToken(self):
        self.assertEqual(fn.metaphoneToken('i'), set(('A',)))
        self.assertEqual(fn.metaphoneToken('don ald'), set(('TN', 'ALT')))
        self.assertEqual(fn.metaphoneToken('goo fy'), set(('K', 'F')))
        self.assertEqual(fn.metaphoneToken('cip ciop'), set(('SP', 'XP')))

    def testWholeSetPredicate(self):
        self.assertEqual(fn.wholeSetPredicate({'i'}), (r"{'i'}",))
        self.assertEqual(fn.wholeSetPredicate({'donald'}), (r"{'donald'}",))
        self.assertEqual(fn.wholeSetPredicate({'goofy'}), (r"{'goofy'}",))
        self.assertEqual(fn.wholeSetPredicate({'cipciop'}), (r"{'cipciop'}",))

    # TODO: test commonSetElementPredicate
    # TODO: test commonTwoElementsPredicate
    # TODO: test commonThreeElementsPredicate
    # TODO: test lastSetElementPredicate
    # TODO: test firstSetElementPredicate

    def testMagnitudeOfCardinality(self):
        self.assertEqual(fn.magnitudeOfCardinality(range(0)), ())
        self.assertEqual(fn.magnitudeOfCardinality(range(98)), ('2',))
        self.assertEqual(fn.magnitudeOfCardinality(range(100)), ('2',))
        self.assertEqual(fn.magnitudeOfCardinality(range(10**6)), ('6',))

    def testLatLongGridPredicate(self):
        self.assertEqual(fn.latLongGridPredicate((1.11, 2.22)), ('[1.1, 2.2]',))
        self.assertEqual(fn.latLongGridPredicate((1.11, 2.27)), ('[1.1, 2.3]',))
        self.assertEqual(fn.latLongGridPredicate((1.18, 2.22)), ('[1.2, 2.2]',))
        self.assertEqual(fn.latLongGridPredicate((1.19, 2.29)), ('[1.2, 2.3]',))
