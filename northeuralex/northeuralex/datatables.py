from sqlalchemy.orm import joinedload
from clld.web import datatables
from clld.web.datatables.base import LinkCol, IntegerIdCol, Col, LinkToMapCol
from clld.web.util.helpers import external_link, link, map_marker_img
from clld.web.util.htmllib import HTML
from clld.web import datatables
from clld.db.meta import DBSession
from clld.db.models.common import Language, Parameter, ValueSet, Value
from clld_glottologfamily_plugin.models import Family
from clld_glottologfamily_plugin.datatables import FamilyCol


from northeuralex.models import Variety, Concept, Word




class Languages(datatables.Languages):
    def base_query(self, query):
        return query.join(Family).options(joinedload(Variety.family)).distinct()

    def col_defs(self):
        return [
            LinkToMapCol(self, 'm'),
            LinkCol(self, 'name'),
            GlottoCodeCol(self, 'glotto_code', model_col=Variety.glottocode),
            IsoCodeCol(self, 'iso_code', model_col=Variety.iso_code),
            FamilyCol(self, 'Family', Variety),
            SubfamilyCol(self, 'subfamily', model_col=Variety.subfamily),
            Col(self,
                'latitude',
                sDescription='<small>The geographic latitude</small>'),
            Col(self,
                'longitude',
                sDescription='<small>The geographic longitude</small>'),
                        
        ]
        
class ConceptsDataTable(datatables.Parameters):

    def col_defs(self):
        return [
            Col(self, 'no.', model_col=Concept.pk),
            ConceptLinkCol(self, 'name', model_col=Concept.english_name),
            Col(self, 'english', model_col=Concept.english_name),
            Col(self, 'german', model_col=Concept.german_name),
            Col(self, 'russian', model_col=Concept.russian_name),
            ConcepticonCol(self, 'concepticon', model_col=Concept.concepticon_name) ]
     
class WordsDataTable(datatables.Values):

    def col_defs(self):
        res = []

        if self.language:
            res.extend([
                Col(self, 'no.', model_col=Concept.pk,
                    get_object=lambda x: x.valueset.parameter),
                ConceptLinkCol(self, 'concept', model_col=Concept.base_name,
                    get_object=lambda x: x.valueset.parameter) ])

        elif self.parameter:
            res.extend([
                VarietyLinkCol(self, 'language', model_col=Variety.name,
                    get_object=lambda x: x.valueset.language) ])

        res.extend([
            Col(self, 'form', model_col=Word.orthography, sTitle='Orthographic form'),
            Col(self, 'raw_ipa', model_col=Word.raw_ipa, sTitle='Automatically generated IPA'),
            # Col(self, 'norm_ipa', model_col=Word.norm_ipa, sTitle='Normalised IPA'),
            StatusCol(self, 'status', model_col=Word.status) ])

        return res


       
            
"""
Columns
"""
class NameCol(LinkCol):
    __kw__ = {'sTitle': 'Name'}
    
    '''def format(self, concept):
        return concept.base_name
    def format(self, concept):
        href = 'http://127.0.0.1:6543/parameters/{}'.format(concept.id)
        return external_link(href, concept.base_name)'''
    
class GlottoCodeCol(Col):
    """
    Custom column to present the glotto_code column of the languages table as a
    link to the respective languoid in Glottolog.
    """

    __kw__ = {'sTitle': 'Glottocode'}

    def format(self, variety):
        href = 'http://glottolog.org/resource/languoid/id/{}'.format(variety.glottocode)
        return external_link(href, variety.glottocode)
        
class IsoCodeCol(Col):
    """
    Custom column to set a proper title for the iso_code column of the
    languages table.
    """

    __kw__ = {'sTitle': 'ISO 639-3'}
    
class SubfamilyCol(Col):
    """
    Custom column to replace the search with a drop-down for the subfamily
    column of the languages table.

    Unlike in, e.g., NextStepCol, the choices have to be set in the constructor
    because otherwise the unit tests do not work.
    """

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = sorted([
            x[0] for x in DBSession.query(Variety.subfamily).distinct()])

        super().__init__(*args, **kwargs)
        
class ConcepticonCol(Col):
    """
    Custom column to present the concepticon_name column of the concepts table
    as a link to the respective concept in the Concepticon.
    """

    __kw__ = {'sTitle': 'Concepticon'}

    def format(self, concept):
        if concept.concepticon_id:
            href = 'http://concepticon.clld.org/parameters/{}'.format(concept.concepticon_id)
            return external_link(href, concept.concepticon_name)
        else:
            return ''
            
class ConceptLinkCol(LinkCol):
    """
    Custom column to present the concept column of the words table as a link
    with a title attribute containing the concept's English name.
    """

    def format(self, item):
        concept = self.get_obj(item)
        if concept:
            return link(self.dt.req, concept, **{'label': concept.base_name})
        else:
            return ''

class VarietyLinkCol(LinkCol):
    """
    Custom column to present the doculect column of the words table as a link
    with a title attribute containing the doculect's family and subfamily.
    """

    def format(self, item):
        variety = self.get_obj(item)
        if variety:
            title = '{} ({}, {})'.format(variety.name,
                        variety.family, variety.subfamily)
            return link(self.dt.req, variety, **{'title': title})
        else:
            return ''

class StatusCol(Col):
    """
    Custom column to replace the search with a drop-down for the status
    column of the words table. Also provides help info in the column's header.
    """

    __kw__ = {
        'sTitle': (
            '<abbr title="'
            'uncertain → certain, questionable → confirmed, unknown status'
            '">Next action</abbr>'),
        'choices': [('certain', 'certain'),
                    ('uncertain', 'uncertain'),
                    ('questionable', 'questionable'),
                    ('confirmed', 'confirmed'),
                    ('unknown status', 'unknown status')] }




def includeme(config):
    """register custom datatables"""

    config.register_datatable('languages', Languages)
    config.register_datatable('parameters', ConceptsDataTable)
    config.register_datatable('values', WordsDataTable)
