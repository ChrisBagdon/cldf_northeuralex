import itertools
import collections

from pycldf import Sources
from clldutils.misc import nfilter
from clldutils.color import qualitative_colors
from clld.cliutil import Data, bibtex2source
from clld.db.meta import DBSession
from clld.db.models import common
from clld.lib import bibtex
from clld.db.util import compute_language_sources
from clld_glottologfamily_plugin.util import load_families

import string
import northeuralex
from northeuralex import models

roles = {'Sources':0, 'Consultants':1, 'Data_Entry':2}
contributors = {}

def add_sources(sources_file_path, session):
    bibtex_db = bibtex.Database.from_file(sources_file_path, encoding='utf-8')
    for record in bibtex_db:
        session.add(bibtex2source(record))
        yield record.id
    session.flush()
def main(args):

    assert args.glottolog, 'The --glottolog option is required!'

    data = Data()
    data.add(
        common.Dataset,
        northeuralex.__name__,
        id=northeuralex.__name__,
        domain='',

        publisher_name="Max Planck Institute for the Science of Human History",
        publisher_place="Jena",
        publisher_url="http://www.shh.mpg.de",
        license="http://creativecommons.org/licenses/by/4.0/",
        jsondata={
            'license_icon': 'cc-by.png',
            'license_name': 'Creative Commons Attribution 4.0 International License'},

    )


    contrib = data.add(
        common.Contribution,
        None,
        id='cldf',
        name=args.cldf.properties.get('dc:title'),
        description=args.cldf.properties.get('dc:bibliographicCitation'),
    )
    # Language table section. Loads data according to cldf-metadata.json. Populates Language, Variety, and LanguageSource tables of SQL DB via the Variety model.
    # Parses Contributor data for latere use.
    for lang in args.cldf.iter_rows('LanguageTable', 'id', 'glottocode', 'ISO639P3code', 'Subfamily', 'name', 'latitude', 'longitude', 'Sources', 'Data_Entry', 'Consultants'):
        data.add(
            models.Variety,
            lang['id'],
            id=lang['id'],
            name=lang['name'],
            latitude=lang['latitude'],
            longitude=lang['longitude'],
            glottocode=lang['glottocode'],
            iso_code=lang['ISO639P3code'],
            subfamily=lang['Subfamily'],
            sources_role=lang['Sources'],
            data_entry=lang['Data_Entry'],
            consultants=lang['Consultants']
        )
        for role in ['Data_Entry', 'Consultants']:
            if lang[role]:
                if len(lang[role].split(';')) > 1:
                    for entry in lang[role].split(';'):
                        stripped_id = entry.replace('.', '').strip()
                        if stripped_id in contributors.keys():
                            contributors[stripped_id].append((stripped_id+role+lang['id'], entry.strip(), roles[role], lang['name']))
                        else:
                            contributors[stripped_id] = [(stripped_id+role+lang['id'], entry.strip(), roles[role], lang['name'])]
                else:
                    stripped_id = lang[role].replace('.', '').strip()
                    if stripped_id in contributors.keys():
                        contributors[stripped_id].append((stripped_id+role+lang['id'], lang[role], roles[role], lang['name']))
                    else:
                        contributors[stripped_id] = [(stripped_id+role+lang['id'], lang[role], roles[role], lang['name'])]
    # Use data from language.csv to populate Contributor and ContributionContributor tables of SQLite db.
    # Items will appear on the website in the order they are added to db, hence the sorting.                 
    for contributor, contributions in sorted(contributors.items()):
        c = data.add(
            common.Contributor,
            contributor,
            # Unique ID built from contributor name + language ID + Role name
            id=contributor,
            name=contributions[0][1],
            description=contributions[0][2]
            )
        for contribution in sorted(contributions, key=lambda con: con[1]):
            con_pk = contribution[3]+contribution[0]
            DBSession.add(common.ContributionContributor(
                contribution_pk = con_pk,
                contributor=c,
                # Used to identify role
                ord=contribution[2]))
   
            
    # Built in functionality to add sources
    for rec in bibtex.Database.from_file(args.cldf.bibpath, lowercase=True):
        data.add(common.Source, rec.id, _obj=bibtex2source(rec))

    refs = collections.defaultdict(list)
    #source_ids = list(add_sources(args.cldf.bibpath, DBSession))
    sources = {s.id: s.pk for s in DBSession.query(common.Source)}
    
    # Parameter table section. Loads data according to cldf-metadata.json. Populates Concept table of SQL DB via the Concept model.
    for param in args.cldf.iter_rows('ParameterTable', 'id', 'concepticonReference', 'name'):
        data.add(
            models.Concept,
            param['id'],
            id=param['id'],
            name='{} [{}]'.format(param['name'], param['id']),
            base_name=param['name'],
            english_name=param['English'],
            german_name=param['German'],
            russian_name=param['Russian'],
            concepticon_id=param['Concepticon_ID'],
            concepticon_name=param['Concepticon_Gloss']
        )
    # Form table section. Loads data according to cldf-metadata.json. Populates ValueSet, ValueSetReference, and Word tables of SQL DB via ValueSet and Word models.
    for form in args.cldf.iter_rows('FormTable', 'ID', 'Form', 'languageReference', 'parameterReference', 'Source', 'Orthography', 'Transliteration', 'Status'):
        vsid = (form['languageReference'], form['parameterReference'])
        vs = data['ValueSet'].get(vsid)
        if not vs:
            vs = data.add(
                common.ValueSet,
                vsid,
                id='-'.join(vsid),
                language=data['Variety'][form['languageReference']],
                parameter=data['Concept'][form['parameterReference']],
                contribution=contrib,
            )
        for ref in form.get('Source', []):
            sid, pages = Sources.parse(ref)
            refs[(vsid, sid)].append(pages)
        data.add(
            models.Word,
            form['ID'],
            id=form['ID'],
            name=form['Form'],
            valueset=vs,
            raw_ipa=form['Form'],
            orthography=form['Orthography'],
            translit=form['Transliteration'],
            status=form['Status']
        )

    for (vsid, sid), pages in refs.items():
        DBSession.add(common.ValueSetReference(
            valueset=data['ValueSet'][vsid],
            source=data['Source'][sid],
            description='; '.join(nfilter(pages))
        ))
    load_families(
        Data(),
        [(l.glottocode, l) for l in data['Variety'].values()],
        glottolog_repos=args.glottolog,
        isolates_icon='tcccccc',
        strict=False,
    )
    



def prime_cache(args):
    """If data needs to be denormalized for lookup, do that here.
    This procedure should be separate from the db initialization, because
    it will have to be run periodically whenever data has been updated.
    """
    # This is required for loading sources in the side bar of the language pages
    compute_language_sources()
