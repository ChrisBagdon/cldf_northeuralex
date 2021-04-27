from zope.interface import implementer
from sqlalchemy import (
    Column,
    String,
    Unicode,
    Integer,
    Boolean,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property

from clld import interfaces
from clld.db.meta import Base, CustomModelMixin
from clld.db.models.common import Language, Parameter, ValueSet, Value
from clld.db.models import common

from clld_glottologfamily_plugin.models import HasFamilyMixin


#-----------------------------------------------------------------------------
# specialized common mapper classes
#-----------------------------------------------------------------------------

@implementer(interfaces.ILanguage)
class Variety(CustomModelMixin, common.Language, HasFamilyMixin):
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    glottocode = Column(Unicode)
    iso_code = Column(Unicode)
    #family = Column(Unicode)
    subfamily = Column(Unicode)

'''


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, common.Parameter):
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)
    concepticon_id = Column(Unicode)


@implementer(interfaces.ILanguage)
class Doculect(CustomModelMixin, Language):
    """
    From Language this model inherits: id, name, latitude (float), longitude
    (float).
    """
    pk = Column(Integer, ForeignKey('language.pk'), primary_key=True)
    iso_code = Column(Unicode)
    glotto_code = Column(Unicode)

    #family = Column(Unicode)
    subfamily = Column(Unicode)
'''


@implementer(interfaces.IParameter)
class Concept(CustomModelMixin, Parameter):
    """
    From Parameter this model inherits: id, name.
    """
    pk = Column(Integer, ForeignKey('parameter.pk'), primary_key=True)

    english_name = Column(Unicode)
    german_name = Column(Unicode)
    russian_name = Column(Unicode)
    base_name = Column(Unicode)
    concepticon_id = Column(Integer)
    concepticon_name = Column(Unicode)



@implementer(interfaces.IValueSet)
class Synset(CustomModelMixin, ValueSet):
    """
    Relevant fields inherited from ValueSet: language, parameter.
    """
    pk = Column(Integer, ForeignKey('valueset.pk'), primary_key=True)



@implementer(interfaces.IValue)
class Word(CustomModelMixin, Value):
    """
    Relevant fields inherited from Value: id, name, valueset.
    """
    pk = Column(Integer, ForeignKey('value.pk'), primary_key=True)

    raw_ipa = Column(Unicode)
    orthography = Column(Unicode)
    translit = Column(Unicode)

    status = Column(Unicode)
