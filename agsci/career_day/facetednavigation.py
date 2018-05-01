from eea.facetednavigation.criteria.handler import Criteria as _Criteria
from eea.facetednavigation.criteria.interfaces import ICriteria
from zope.interface import implementer
from eea.facetednavigation.widgets.storage import Criterion
from eea.facetednavigation.config import ANNO_CRITERIA
from zope.annotation.interfaces import IAnnotations
from persistent.list import PersistentList
from eea.facetednavigation.settings.interfaces import IDontInheritConfiguration
from zope.globalrequest import getRequest
from Products.CMFCore.utils import getToolByName

from content import IEmployer

@implementer(ICriteria)
class Criteria(_Criteria):

    def getFields(self):

        fields = ['majors', 'positions_available']

        for (key, field) in IEmployer.namesAndDescriptions():

            if key in fields:

                # Set the cid to the key, minus underscores.
                cid = key
                cid = cid.replace('_', '')

                # Get the vocabulary name
                try:
                    value_type = field.value_type
                except AttributeError:
                    vocabulary_name = ""
                    catalog = "portal_catalog"
                else:
                    vocabulary_name = value_type.vocabularyName
                    catalog = ""

                # Title is the field title
                title = field.title

                yield Criterion(
                    _cid_=cid,
                    widget="checkbox",
                    title=title,
                    index=key,
                    operator="or",
                    operator_visible=False,
                    vocabulary=vocabulary_name,
                    position="right",
                    section="default",
                    hidden=False,
                    count=True,
                    catalog=catalog,
                    sortcountable=False,
                    hidezerocount=False,
                    maxitems=50,
                    sortreversed=False,
                )

    @property
    def request(self):
        return getRequest()

    # Caching call for criteria on request, so we don't have to recalculate
    # each time.
    def _criteria(self):
        cache = IAnnotations(self.request)
        key = 'eea.facetednav.%s' % self.context.UID()

        if not cache.has_key(key):
            cache[key] = self.__criteria()

        return cache[key]

    def __criteria(self):

        criteria = [
                Criterion(
                    widget="criteria",
                    title="Current search",
                    position="center",
                    section="default",
                    hidden=False,
                ),
                Criterion(
                    _cid_="SearchableText",
                    widget="text",
                    title="Search Employers",
                    index="SearchableText",
                    position="right",
                    section="default",
                    wildcard=True,
                    onlyallelements=True,
                    hidden=False,
                )
        ]

        criteria.extend(self.getFields())

        return PersistentList(criteria)

