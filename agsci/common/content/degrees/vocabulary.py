from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

@implementer(IVocabularyFactory)
class StaticVocabulary(object):

    preserve_order = False

    items = ['N/A',]

    def __call__(self, context):

        items = self.items

        if not self.preserve_order:
            items = list(set(self.items))
            items.sort()

        terms = [SimpleTerm(x,title=x) for x in items]

        return SimpleVocabulary(terms)

@implementer(IVocabularyFactory)
class KeyValueVocabulary(object):

    items = [
        ('N/A', 'N/A'),
    ]

    def __call__(self, context):

        return SimpleVocabulary(
            [
                SimpleTerm(x, title=y) for (x, y) in self.items
            ]
        )

class InterestAreaVocabulary(StaticVocabulary):

    items = [
        u'Animal',
        u'Plant',
        u'Environment, Sustainability, Nature',
        u'Science',
        u'Business',
        u'Health and Medicine',
        u'Engineering',
        u'Education',
        u'Food',
        u'Policy and Regulatory Affairs',
    ]

class CareerVocabulary(StaticVocabulary):

    items = [
        u"Ag Science Educator",
        u"Agricultural Engineer",
        u"Agricultural Loan Officer",
        u"Animal Welfare Inspector",
        u"Aquaponics/Hyrdroponics Producer",
        u"Arborist",
        u"Athletic Field / Turf Manager",
        u"Biologist",
        u"Biomedical Researcher",
        u"Biosecurity Engineer",
        u"Corporate Sustainability Officer",
        u"Economic Development Coordinator",
        u"Environmental Consultant",
        u"Environmental Engineer",
        u"Extension Educator",
        u"Farm Manager",
        u"Food Scientist",
        u"Forensic Toxicologist",
        u"Forester",
        u"Game Warden/Conservation Officer",
        u"GIS Analyst",
        u"Golf Course Superintendent",
        u"Government Policy Advocate",
        u"Greenhouse Manager",
        u"Horticulturist",
        u"Hydrologist",
        u"Immunologist",
        u"Industry Sales Representative",
        u"Landscape Designer",
        u"Medical Doctor",
        u"Organic Farm Certification Specialist",
        u"Peace Corps Volunteer",
        u"Pharmacist",
        u"Plant Scientist",
        u"Production/Manufacturing Manager",
        u"Quality Assurance Manager",
        u"Renewable Energy Consultant",
        u"Risk Management Specialist",
        u"Urban Planner",
        u"Veterinarian",
        u"Wildland Firefighter",
        u"Wildlife Biologist",
        u"Zookeeper",
    ]

class ClubVocabulary(StaticVocabulary):

    items = [
        "1/4 Scale Tractor Pulling Team (Penn State Pullers)",
        "Ag Advocates",
        "Ag Avengers",
        "Ag Student Council",
        "Ag Systems Management Club",
        "Agribusiness Management Club",
        "Agronomy Club",
        "Alpha Gamma Rho (AGR)",
        "Alpha Tau Alpha, Eta Chapter",
        "Alpha Zeta (AZ)",
        "American Society of Agricultural and Biological Engineers (ASABE)",
        "Beekeepers Club",
        "Biomedical Sciences Club",
        "Block and Bridle Club",
        "Blooms and Shrooms",
        "Cheese Club",
        "Coaly Society",
        "Collegiate 4-H",
        "Collegiate Cattlewomen",
        "Collegiate Dairy Products Evaluation Team",
        "Collegiate Farm Bureau",
        "Community, Environment, and Development Club",
        "Dairy Cattle Judging Team",
        "Dairy Science Club",
        "Delta Theta Sigma (DTS)",
        "Dressage Team",
        "EARTH House",
        "Environmental Resource Management Society",
        "Equestrian Team",
        "Flower Judging Team",
        "Fly Fishing Club",
        "Food Science Club",
        "Food Science College Bowl Team",
        "Horse Judging Team",
        "Horticulture Club",
        "International Ag Club",
        "Lead Society",
        "Literacy, Education, and Agricultural Development Society",
        "Livestock Judging Team",
        "Meat Judging Team",
        "Minorities in Agriculture, Natural Resources and Related Sciences (MANRRS)",
        "National Agri-Marketing Association (NAMA)",
        "Penn State AgriMarketing Team (NAMA)",
        "Penn State Environmental Society",
        "Penn State Equine Research Team",
        "Penn State International Genetically Engineered Machine Competition (iGEM)",
        "Penn State Pullers",
        "Penn State Reproduction Research Team",
        "Penn State Spur Collectors",
        "Poultry Judging Team",
        "Poultry Science Club",
        "Pre-Med Club",
        "Pre-Vet Club",
        "Sigma Alpha",
        "Small and Exotic Animal Club (SEAC)",
        "Society of American Foresters (SAF)",
        "Soil Judging Team",
        "Student Farm Club",
        "Students for Cultivating Change",
        "Sustainable Agriculture Club",
        "Tau Phi Delta (Treehouse)",
        "Teach Ag! Society",
        "The Collegiate Horseman's Association at Penn State (CHAPS)",
        "The Penn State Spur Collectors",
        "The Wildlife Society (TWS)",
        "Turf Club",
        "Turf Judging Team - GCSAA",
        "Turf Judging Team - STMA",
        "Weed Science Team",
        "Woodsmen Team"
    ]

InterestAreaVocabularyFactory = InterestAreaVocabulary()
CareerVocabularyFactory = CareerVocabulary()
ClubVocabularyFactory = ClubVocabulary()
