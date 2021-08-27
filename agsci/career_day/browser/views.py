from eea.facetednavigation.browser.app.query import FacetedQueryHandler
from eea.facetednavigation.caching import ramcache
from eea.facetednavigation.caching import cacheKeyFacetedNavigation
from eea.facetednavigation.interfaces import ICriteria
from plone.app.textfield.value import RichTextValue
from plone.dexterity.utils import createContentInContainer
from plone.namedfile.file import NamedBlobImage
from BeautifulSoup import BeautifulSoup
from Products.agCommon import ploneify
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getUtility, getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.schema.interfaces import IVocabularyFactory

import csv
import re
import requests


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

class ImportEmployersView(BaseView):
    pass

class ProcessImportEmployersView(BaseView):

    valid_image_types = ('image/png', 'image/jpeg', 'image/gif')

    transforms = {
        'interested_in_students_in_the_following_program_areas_check_all_that_may_apply' : 'majors',
        'please_upload_company_logo_here_jpeg_or_gif_format' : 'image',
        'company_description_please_limit_to_space_provided_100200_words' : 'description',
        'my_organization_is_interested_in_recruiting_students_in_the_following_class_levels_check_all_that_apply' : 'class_year',
        'company_name' : 'title',
        'company' : 'title',
        'positions_available_check_all_that_may_apply' : 'positions_available',
        'organization_company_web_site_url' : 'website',
        'organization_company_website' : 'website',
        'registration_type' : 'registration_type',
        'interested_in_recruiting_for_the_following_positions' : 'positions_available',
        'interested_in_recruiting_for_class_level' : 'class_year',
        'majors_interested_in_recruiting' : 'majors',
        'organization_description_to_be_included_in_event_materials_please_limit_to_space_provided_max_200_words' : 'description',
        'please_upload_a_high_resolution_organization_logo_here_jpeg_or_gif_format' : 'image',
    }

    def format_key(self, name):
        first_cap_re = re.compile('(.)([A-Z][a-z]+)')
        all_cap_re = re.compile('([a-z0-9])([A-Z])')
        whitespace_re = re.compile('\s+')
        nonalpha_re = re.compile('[^A-Za-z0-9_ ]+')
        underscore_re = re.compile('_+')

        name = name.strip()
        name = nonalpha_re.sub('', name)
        name = whitespace_re.sub('_', name)
        name = first_cap_re.sub(r'\1_\2', name)
        name = all_cap_re.sub(r'\1_\2', name).lower()
        name = underscore_re.sub('_', name)

        return self.transforms.get(name, '')

    def process_csv(self, csv_file):

        data = []

        filename = csv_file.name

        reader = csv.reader(open(filename, 'rU'), delimiter=',', quotechar='"')

        rows = [x for x in reader]

        headers = rows.pop(0)
        headers = [self.format_key(x) for x in headers]

        for row in rows:

            decoded_row = [x.decode('cp1252') for x in row]

            _ = dict(zip(headers, decoded_row))

            if _.has_key(''):
                del _['']

            for k in ['class_year', 'majors', 'positions_available']:
                if _.has_key(k):
                    _[k] = [x.strip() for x in _[k].split(',')]
                    _[k] = self.vocab_filter(k, _[k])

            # Website
            website = _.get('website', None)

            if website:
                if not website.startswith(('http://', 'https://')):
                    _['website'] = 'http://%s' % website

            data.append(_)

        return data

    def get_image_url(self, image):
        if image:
            image = image.strip()

            if image.startswith('<a'):
                soup = BeautifulSoup(image)
                href = soup.find('a').get('href', '')

                if href:
                    return href

            return image

    def get_image(self, _):
        image = _.get('image', None)

        if image:

            image_url = self.get_image_url(image)

            try:
                response = requests.get(image_url)
            except:
                pass
            else:


                if response.status_code in [200]:
                    if response.headers.get('Content-Type', None) in self.valid_image_types:
                        return response.content
                    else:
                        print "ERROR in Content-Type: %s" % image_url

    def get_vocab_values(self, field):

        f2v = {
            'majors' : 'agsci.career_day.major',
            'positions_available' : 'agsci.career_day.positions_available',
            'class_year' : 'agsci.career_day.class_year',
        }

        vocab_name = f2v.get(field, None)

        if vocab_name:

            vocab = getUtility(IVocabularyFactory, vocab_name)

            values = vocab(self.context)

            if values:

                values = [x.value for x in values]

                return values

        return []

    def vocab_filter(self, k, v):

        values = self.get_vocab_values(k)

        # Remove 'Other' positions available
        if k in ('positions_available',):
            for i in range(0, len(v)):
                if v[i].startswith('Other'):
                    v[i] = 'Other'

        if values:
            invalid_values = set(v) - set(values)

            if invalid_values:
                raise ValueError(u"Invalid values for %s: %r" % (k, list(invalid_values)))

            v = set(values) & set(v)

            return list(v)

        return []


    def __call__(self):

        imported_count = 0

        csv_file = self.request.form.get('csv', None)

        if csv_file:
            data = self.process_csv(csv_file)

            if data:
                for _ in data:
                    title = _['title']

                    _id = ploneify(title)

                    if _id not in self.context.objectIds():

                        description = _['description']
                        majors = _['majors']
                        positions_available = _['positions_available']
                        class_year = _['class_year']
                        website = _['website']

                        kwargs = {
                            'title' : title,
                            'description' : description,
                            'majors' : majors,
                            'positions_available' : positions_available,
                            'class_year' : class_year,
                            'website' : website,
                        }

                        item = createContentInContainer(
                            self.context,
                            'employer',
                            id=_id,
                            **kwargs)

                        image_data = self.get_image(_)

                        if image_data:
                            img = NamedBlobImage()
                            img.data = image_data
                            item.image = img

                        imported_count = imported_count + 1

        return 'Imported %d items' % imported_count
