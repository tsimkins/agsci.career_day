from plone.supermodel import model
from zope import schema
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile
from zope.interface import Interface, provider, invariant, Invalid, implementer, implements
from plone.app.content.interfaces import INameFromTitle
from agsci.syllabus import syllabusMessageFactory as _
from zope.component import adapter
from plone.namedfile.field import NamedBlobImage

@provider(IFormFieldProvider)
class IEmployerContainer(model.Schema):
    pass
    
@provider(IFormFieldProvider)
class IEmployer(model.Schema):

    majors = schema.List(
        title=_(u"Major(s)"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.career_day.major"),
        required=True,
    )

    website = schema.TextLine(
        title=_(u"Employer Website"),
        description=_(u""),
        required=False,
    )
    
    image = NamedBlobImage(
        title=_(u"Employer Logo"),
        description=_(u""),
        required=False,
    )

