from eea.facetednavigation.browser.app.query import FacetedQueryHandler
from eea.facetednavigation.caching import ramcache
from eea.facetednavigation.caching import cacheKeyFacetedNavigation
from plone.app.textfield.value import RichTextValue
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory

from ..content import IEmployer

class BaseView(BrowserView):

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

class EmployerView(BaseView):

    pass

class PloneSiteView(BaseView):

    def getQuery(self):
        return {'Type' : 'Employer', 'sort_on' : 'sortable_title'}

    def getFolderContents(self):
        return self.portal_catalog.searchResults(self.getQuery())


class PloneSiteFacetedQueryHandler(PloneSiteView, FacetedQueryHandler):

    def criteria(self, sort=False, **kwargs):
        query = self.getQuery()
        faceted_query = super( PloneSiteFacetedQueryHandler, self).criteria(sort, **kwargs)
        query.update(faceted_query)
        return query

    @ramcache(cacheKeyFacetedNavigation, dependencies=['eea.facetednavigation'])
    def __call__(self, *args, **kwargs):
        kwargs['batch'] = False
        self.brains = self.query(**kwargs)
        html = self.index()
        return html