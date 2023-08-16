from plone.supermodel import model
from zope import schema
from plone.app.textfield import RichText
from plone.autoform import directives as form
from plone.autoform.interfaces import IFormFieldProvider
from plone.namedfile.field import NamedBlobFile
from zope.interface import Interface, provider, invariant, Invalid, implementer, implements
from plone.app.content.interfaces import INameFromTitle
from zope.component import adapter
from plone.namedfile.field import NamedBlobImage

from .. import career_dayMessageFactory as _

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

    class_year = schema.List(
        title=_(u"Class Year(s)"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.career_day.class_year"),
        required=True,
    )

    positions_available = schema.List(
        title=_(u"Position(s) Available"),
        description=_(u""),
        value_type=schema.Choice(vocabulary="agsci.career_day.positions_available"),
        required=True,
    )

    website = schema.TextLine(
        title=_(u"Employer Website"),
        description=_(u""),
        required=False,
    )
