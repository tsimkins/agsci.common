from agsci.common.content.vocabulary import StaticVocabulary, KeyValueVocabulary

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
        ('plain', 'Plain'),
    ]

class FeatureCardStyleVocabulary(KeyValueVocabulary):
    items = [
        ('news', 'News Items'),
        ('events', 'Events'),
        ('pages', 'Pages'),
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
            (x.getId, x.Title) for x in results
        ]

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
    ]

ButtonColorsVocabularyFactory = ButtonColorsVocabulary()
CTABackgroundVocabularyFactory = CTABackgroundVocabulary()
LRAlignVocabularyFactory = LRAlignVocabulary()
LCAlignVocabularyFactory = LCAlignVocabulary()
CardStyleVocabularyFactory = CardStyleVocabulary()
FeatureCardStyleVocabularyFactory = FeatureCardStyleVocabulary()
PeopleVocabularyFactory = PeopleVocabulary()
VideoAspectRatioVocabularyFactory = VideoAspectRatioVocabulary()
HVOrientationVocabularyFactory = HVOrientationVocabulary()
SocialMediaPlatformVocabularyFactory = SocialMediaPlatformVocabulary()