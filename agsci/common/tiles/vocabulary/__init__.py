from agsci.common.content.vocabulary import KeyValueVocabulary

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
    ]

class LRAlignVocabulary(KeyValueVocabulary):
    items = [
        ('left', 'Left'),
        ('right', 'Right'),
    ]

class CardStyleVocabulary(KeyValueVocabulary):
    items = [
        ('news', 'News Items'),
        ('events', 'Events'),
        ('pages', 'Pages'),
    ]

ButtonColorsVocabularyFactory = ButtonColorsVocabulary()
CTABackgroundVocabularyFactory = CTABackgroundVocabulary()
LRAlignVocabularyFactory = LRAlignVocabulary()
CardStyleVocabularyFactory = CardStyleVocabulary()