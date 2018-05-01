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
        'Agribusiness Management',
        'Agricultural and Extension Education',
        'Agricultural Science',
        'Animal Science',
        'Biological Engineering',
        'BioRenewable Systems',
        'Community, Environment, and Development',
        'Environmental Resource Management',
        'Food Science',
        'Forest Ecosystem Management',
        'Immunology and Infectious Disease',
        'Landscape Contracting',
        'Plant Sciences',
        'Toxicology',
        'Turfgrass Science',
        'Veterinary and Biomedical Sciences',
        'Wildlife and Fisheries Science',
        'Forest Technology',
        'Turfgrass Science and Management (Online)',
        'Wildlife Technology'
    ]

MajorVocabularyFactory = MajorVocabulary()