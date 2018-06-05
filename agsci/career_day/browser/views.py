from eea.facetednavigation.browser.app.query import FacetedQueryHandler
from eea.facetednavigation.caching import ramcache
from eea.facetednavigation.caching import cacheKeyFacetedNavigation
from eea.facetednavigation.interfaces import ICriteria
from plone.app.textfield.value import RichTextValue
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility, getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory

from ..content import IEmployer

class BaseView(BrowserView):

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def anonymous(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.anonymous()

class EmployerView(BaseView):

    @property
    def description(self):
        return self.context.Description()

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

    def sorted_field_values(self, field, vocab_name):

        v = getattr(self.context, field, [])

        if v and isinstance(v, (list, tuple)):

            vocab = getUtility(IVocabularyFactory, vocab_name)

            values = vocab(self.context)

            if values:

                values = [x.value for x in values]

                def sort_key(x):

                    try:
                        return values.index(x)
                    except (ValueError, IndexError):
                        return 99999

                return sorted(v, key=sort_key)

        return []

    @property
    def class_year(self):
        return self.sorted_field_values(
            'class_year',
            'agsci.career_day.class_year'
        )

    @property
    def positions_available(self):
        return self.sorted_field_values(
            'positions_available',
            'agsci.career_day.positions_available'
        )

    @property
    def website(self):
        return getattr(self.context, 'website', None)

    @property
    def parent_url(self):
        return self.context.aq_parent.absolute_url()

class EmployerContainerView(BaseView):

    def getQuery(self):
        return {'Type' : 'Employer', 'sort_on' : 'sortable_title'}

    def getFolderContents(self):
        return self.portal_catalog.searchResults(self.getQuery())

    def get_html(self, r):
        o = r.getObject()
        v = o.restrictedTraverse('@@content')
        return v()

class PloneSiteFacetedQueryHandler(EmployerContainerView, FacetedQueryHandler):

    @property
    def faceted_query(self, sort=False, **kwargs):
        return super( PloneSiteFacetedQueryHandler, self).criteria(sort, **kwargs)

    @property
    def filtered_results(self):
        keys = self.faceted_query.keys()

        criteria = ICriteria(self.context)

        for cid, criterion in criteria.items():
            try:
                idx = criterion.index
            except AttributeError:
                pass # Not index-based
            else:
                if idx in keys:
                    return True

    def criteria(self, sort=False, **kwargs):
        query = self.getQuery()
        query.update(self.faceted_query)
        return query

    @ramcache(cacheKeyFacetedNavigation, dependencies=['eea.facetednavigation'])
    def __call__(self, *args, **kwargs):

        if not self.filtered_results:
            self.brains = []
        else:
            kwargs['batch'] = False
            self.brains = self.query(**kwargs)

        return self.index()
