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

    @property
    def has_logo(self):
        logo = getattr(self.context, 'image', None)

        if logo and hasattr(logo, 'size') and logo > 0:
            return True

        return False

    def tag(self, css_class='', scale='leadimage'):

        if self.has_logo:
            alt = u'%s Logo' % self.context.Title()
            images = self.context.restrictedTraverse('@@images')

            return images.tag('image', scale=scale, alt=alt, css_class=css_class)

        return ''

    @property
    def majors(self):
        v = getattr(self.context, 'majors', [])

        if v and isinstance(v, (list, tuple)):
            return sorted(v)

        return []

    @property
    def positions_available(self):
        v = getattr(self.context, 'positions_available', [])

        if v and isinstance(v, (list, tuple)):

            vocab = getUtility(IVocabularyFactory, "agsci.career_day.positions_available")

            values = vocab(self.context)

            if values:

                values = [x.value for x in values]

                def sort_key(x):

                    try:
                        return values.index(x)
                    except IndexError:
                        return 99999

                return sorted(v, key=sort_key)

        return []

    @property
    def website(self):
        return getattr(self.context, 'website', None)

    @property
    def parent_url(self):
        return self.context.aq_parent.absolute_url()

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