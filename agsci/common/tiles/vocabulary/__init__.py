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

ButtonColorsVocabularyFactory = ButtonColorsVocabulary()
CTABackgroundVocabularyFactory = CTABackgroundVocabulary()