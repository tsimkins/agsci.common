from Products.CMFCore.utils import getToolByName
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from zope.interface import directlyProvides, implements
from datetime import datetime, timedelta

class StaticVocabulary(object):

    implements(IVocabularyFactory)

    preserve_order = False

    items = ['N/A',]

    def __call__(self, context):

        items = self.items

        if not self.preserve_order:
            items = list(set(self.items))
            items.sort()

        terms = [SimpleTerm(x,title=x) for x in items]

        return SimpleVocabulary(terms)

class KeyValueVocabulary(object):

    implements(IVocabularyFactory)

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
        'Animals',
        'Business',
        'Environment',
        'Human Health',
        'Plants',
        'Science',
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
        'Horse Judging Team',
        'Meat Judging Team',
        'Penn State International Genetically Engineered Machine Competition (iGEM)',
        'Penn State Pullers',
        'Pre-Med Club',
        'Alpha Tau Alpha, Eta Chapter',
        'National Agri-Marketing Association (NAMA)',
        'Ag Advocates',
        'Agribusiness Management Club',
        'Ag Student Council',
        'Ag Systems Management Club',
        'Agronomy Club',
        'Beekeepers Club',
        'Biomedical Sciences Club',
        'Block and Bridle Club',
        'Blooms and Shrooms',
        'Cheese Club',
        "The Collegiate Horseman's Association at Penn State (CHAPS)",
        'Collegiate Cattlewomen',
        'Collegiate 4-H',
        'Collegiate Farm Bureau',
        'Community, Environment, and Development Club',
        'Dairy Science Club',
        'EARTH House',
        'Environmental Resource Management Society',
        'Penn State Equine Research Team',
        'Fly Fishing Club',
        'Food Science Club',
        'Horticulture Club',
        'Literacy, Education, and Agricultural Development Society',
        'Penn State Reproduction Research Team',
        'Poultry Science Club',
        'Pre-Vet Club',
        'Small and Exotic Animal Club (SEAC)',
        'The Penn State Spur Collectors',
        'Student Farm Club',
        'Students for Cultivating Change',
        'International Ag Club',
        'Sustainable Agriculture Club',
        'Teach Ag! Society',
        'Turf Club',
        '1/4 Scale Tractor Pulling Team (Penn State Pullers)',
        'Collegiate Dairy Products Evaluation Team',
        'Dairy Cattle Judging Team',
        'Dressage Team',
        'Equestrian Team',
        'Food Science College Bowl Team',
        'Horse Judging',
        'Livestock Judging Team',
        'Penn State AgriMarketing Team (NAMA)',
        'Poultry Judging Team',
        'Soil Judging Team',
        'Turf Judging Team - GCSAA',
        'Turf Judging Team - STMA',
        'Weed Science Team',
        'Woodsmen Team',
        'Alpha Gamma Rho (AGR)',
        'Alpha Zeta (AZ)',
        'Delta Theta Sigma (DTS)',
        'Tau Phi Delta (Treehouse)',
        'Sigma Alpha',
        'American Society of Agricultural and Biological Engineers (ASABE)',
        'American Water Resources Association (AWRA)',
        'Coaly Society',
        'Forest Products Society (FPS)',
        'Minorities in Agriculture, Natural Resources and Related Sciences (MANRRS)',
        'Society of American Foresters (SAF)',
        'The Wildlife Society (TWS)',
    ]

InterestAreaVocabularyFactory = InterestAreaVocabulary()
CareerVocabularyFactory = CareerVocabulary()
ClubVocabularyFactory = ClubVocabulary()