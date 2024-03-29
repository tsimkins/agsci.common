from agsci.common.content.vocabulary import StaticVocabulary

class CountyVocabulary(StaticVocabulary):

    preserve_order = True

    items = [
        u"N/A",
        u"Adams",
        u"Allegheny",
        u"Armstrong",
        u"Beaver",
        u"Bedford",
        u"Berks",
        u"Blair",
        u"Bradford",
        u"Bucks",
        u"Butler",
        u"Cambria",
        u"Cameron",
        u"Carbon",
        u"Centre",
        u"Chester",
        u"Clarion",
        u"Clearfield",
        u"Clinton",
        u"Columbia",
        u"Crawford",
        u"Cumberland",
        u"Dauphin",
        u"Delaware",
        u"Elk",
        u"Erie",
        u"Fayette",
        u"Forest",
        u"Franklin",
        u"Fulton",
        u"Greene",
        u"Huntingdon",
        u"Indiana",
        u"Jefferson",
        u"Juniata",
        u"Lackawanna",
        u"Lancaster",
        u"Lawrence",
        u"Lebanon",
        u"Lehigh",
        u"Luzerne",
        u"Lycoming",
        u"McKean",
        u"Mercer",
        u"Mifflin",
        u"Monroe",
        u"Montgomery",
        u"Montour",
        u"Northampton",
        u"Northumberland",
        u"Perry",
        u"Philadelphia",
        u"Pike",
        u"Potter",
        u"Schuylkill",
        u"Snyder",
        u"Somerset",
        u"Sullivan",
        u"Susquehanna",
        u"Tioga",
        u"Union",
        u"Venango",
        u"Warren",
        u"Washington",
        u"Wayne",
        u"Westmoreland",
        u"Wyoming",
        u"York",
    ]

# Factories
CountyVocabularyFactory = CountyVocabulary()