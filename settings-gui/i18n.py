#!/usr/bin/env python3
"""
Internationalization (i18n) module for Lotus Settings GUI.
Loads translations from gettext .po files.
"""

import os
import sys
import gettext as gt
from pathlib import Path

# Get the base directory of the project
BASE_DIR = Path(__file__).parent.parent
LOCALE_DIR = BASE_DIR / "po"

# Try to load translations
_translations = {}


def init_translations(locale: str = None):
    """
    Initialize translations for the specified locale.

    Args:
        locale: Locale code (e.g., 'vi', 'en'). If None, uses system locale.
    """
    global _translations

    if locale is None:
        # Try to get from environment
        locale = os.environ.get("LANG", "en").split(".")[0]

    # Try to find the translation
    try:
        trans = gt.translation(
            "fcitx5-lotus", localedir=str(LOCALE_DIR), languages=[locale]
        )
        _translations[locale] = trans
    except FileNotFoundError:
        # Fall back to English (null translation)
        _translations[locale] = gt.NullTranslations()


def gettext(message: str, locale: str = None) -> str:
    """
    Translate a message using gettext.

    Args:
        message: The message to translate.
        locale: Optional locale override.

    Returns:
        Translated message.
    """
    global _translations

    if locale is None:
        locale = os.environ.get("LANG", "en").split(".")[0]

    if locale not in _translations:
        init_translations(locale)

    return _translations.get(locale, gt.NullTranslations()).gettext(message)


def ngettext(singular: str, plural: str, n: int, locale: str = None) -> str:
    """
    Translate a message with plural forms.

    Args:
        singular: Singular form.
        plural: Plural form.
        n: Number for plural selection.
        locale: Optional locale override.

    Returns:
        Translated message.
    """
    global _translations

    if locale is None:
        locale = os.environ.get("LANG", "en").split(".")[0]

    if locale not in _translations:
        init_translations(locale)

    return _translations.get(locale, gt.NullTranslations()).ngettext(
        singular, plural, n
    )


# Shortcut function
_ = gettext

# Initialize with default locale
init_translations()
