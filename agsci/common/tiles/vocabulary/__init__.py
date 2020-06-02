from agsci.common.content.vocabulary import StaticVocabulary, KeyValueVocabulary
from agsci.common.utilities import getExtensionConfig

class ButtonColorsVocabulary(KeyValueVocabulary):
    items = [
        ('orange', 'Orange'),
        ('green', 'Green'),
        ('purple', 'Purple'),
    ]

class CTABackgroundVocabulary(KeyValueVocabulary):
    items = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('none', 'No Background'),
    ]

class LRAlignVocabulary(KeyValueVocabulary):
    items = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]

class LCAlignVocabulary(KeyValueVocabulary):
    items = [
        ('left', 'Left'),
        ('center', 'Center'),
    ]

class HVOrientationVocabulary(KeyValueVocabulary):
    items = [
        ('vertical', 'Vertical'),
        ('horizontal', 'Horizontal'),
    ]

class CardStyleVocabulary(KeyValueVocabulary):
    items = [
        ('image', 'Image'),
        ('image_description', 'Image and Description'),
        ('image_plain', 'Image (Plain)'),
        ('links', 'Links'),
        ('plain', 'Plain'),
    ]

class FeatureCardStyleVocabulary(KeyValueVocabulary):
    items = [
        ('news', 'News Items'),
        ('news-condensed', 'News Items (Condensed)'),
        ('events', 'Events'),
        ('pages', 'Pages'),
        ('cards', 'Cards'),
        ('cards-condensed', 'Cards (Condensed)'),
    ]

class PeopleVocabulary(KeyValueVocabulary):

    preserve_order = True

    @property
    def items(self):
        results = self.portal_catalog.searchResults({
            'Type' : 'Person',
            'sort_on' : 'sortable_title',
        })

        return [
            (x.getId, x.sortable_title_case) for x in results
        ]

class TagsVocabulary(StaticVocabulary):

    prefixes = [
        'majors',
        'news',
    ]

    @property
    def items(self):
        return [x for x in self.portal_catalog.uniqueValuesFor('Subject') if any([x.startswith('%s' % y) for y in self.prefixes])]

class PublicTagsVocabulary(StaticVocabulary):

    @property
    def items(self):
        return self.portal_catalog.uniqueValuesFor('Tags')

class VideoAspectRatioVocabulary(StaticVocabulary):

    items = [
        u'16:9',
        u'3:2',
        u'4:3',
    ]

class SocialMediaPlatformVocabulary(KeyValueVocabulary):

    preserve_order = True

    items = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('newsletter', 'Newsletter'),
    ]

class AgJourneyQuoteStyleVocabulary(KeyValueVocabulary):
    items = [
        ('plain_image_left', 'Plain (Image Left)'),
        ('plain_image_right', 'Plain (Image Right)'),
        ('plain_image_none', 'Plain (No Image)'),
        ('image_large', 'Large Image'),
        ('handwriting_small', 'Handwriting (Small)'),
        ('handwriting_large', 'Handwriting (Large)'),
    ]

class ExtensionListingProductTypesVocabulary(StaticVocabulary):

    @property
    def items(self):
        config = getExtensionConfig()
        return sorted(set([x.get('product_type', None) for x in config if x.get('product_type', None)]))

ButtonColorsVocabularyFactory = ButtonColorsVocabulary()
CTABackgroundVocabularyFactory = CTABackgroundVocabulary()
LRAlignVocabularyFactory = LRAlignVocabulary()
LCAlignVocabularyFactory = LCAlignVocabulary()
CardStyleVocabularyFactory = CardStyleVocabulary()
FeatureCardStyleVocabularyFactory = FeatureCardStyleVocabulary()
PeopleVocabularyFactory = PeopleVocabulary()
TagsVocabularyFactory = TagsVocabulary()
PublicTagsVocabularyFactory = PublicTagsVocabulary()
VideoAspectRatioVocabularyFactory = VideoAspectRatioVocabulary()
HVOrientationVocabularyFactory = HVOrientationVocabulary()
SocialMediaPlatformVocabularyFactory = SocialMediaPlatformVocabulary()
AgJourneyQuoteStyleVocabularyFactory = AgJourneyQuoteStyleVocabulary()
ExtensionListingProductTypesVocabularyFactory = ExtensionListingProductTypesVocabulary()