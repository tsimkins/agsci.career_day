from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides, implements
from datetime import datetime, timedelta

class StaticVocabulary(object):

    implements(IVocabularyFactory)

    preserve_order = False

    items = ['N/A',]

    def __call__(self, context):

        items = self.items

        if not self.preserve_order:
            items = list(set(self.items))
            items.sort()

        terms = [SimpleTerm(x,title=x) for x in items]

        return SimpleVocabulary(terms)

class KeyValueVocabulary(object):

    implements(IVocabularyFactory)

    items = [
        ('N/A', 'N/A'),
    ]

    def __call__(self, context):

        return SimpleVocabulary(
            [
                SimpleTerm(x, title=y) for (x, y) in self.items
            ]
        )

class MajorVocabulary(StaticVocabulary):

    items = [
        u'Agribusiness Management',
        u'Agricultural & Extension Education',
        u'Agricultural Science',
        u'Animal Science',
        u'Biological Engineering',
        u'BioRenewable Systems',
        u'Community Environment & Development',
        u'Environmental Resource Management',
        u'Food Science',
        u'Forest Ecosystem Management',
        u'Immunology & Infectious Disease',
        u'Landscape Contracting',
        u'Plant Sciences',
        u'Toxicology',
        u'Turfgrass Science',
        u'Veterinary & Biomedical Sciences',
        u'Wildlife & Fisheries Science',
    ]

class ClassYearVocabulary(StaticVocabulary):

    preserve_order = True

    items = [
        u'Senior',
        u'Junior',
        u'Sophomore',
        u'Freshman'
    ]

class PositionsAvailableVocabulary(StaticVocabulary):

    preserve_order = True

    items = [
        u'Full Time',
        u'Part Time',
        u'Internship',
        u'Externship',
        u'Seasonal',
        u'Co-op',
        u'Other',
    ]

MajorVocabularyFactory = MajorVocabulary()
ClassYearVocabularyFactory = ClassYearVocabulary()
PositionsAvailableVocabularyFactory = PositionsAvailableVocabulary()