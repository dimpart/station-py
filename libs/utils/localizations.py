# -*- coding: utf-8 -*-
# ==============================================================================
# MIT License
#
# Copyright (c) 2023 Albert Moky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================

from typing import Optional, Union

from dimples.utils import StringPairing
from dimples import Visa
from dimples.database.dos.base import template_replace


class Locale:

    def __init__(self, language: str, script: str = None, country: str = None):
        super().__init__()
        self.__language = language
        self.__script = script
        self.__country = country

    @property
    def language(self) -> str:
        return self.__language

    @property
    def script(self) -> Optional[str]:
        return self.__script

    @property
    def country(self) -> Optional[str]:
        return self.__country

    # Override
    def __str__(self) -> str:
        language = self.__language
        script = self.__script
        country = self.__country
        assert len(language) > 0, 'locale error: %s, %s, %s' % (language, script, country)
        if script is not None and len(script) > 0:
            assert country is not None and len(country) > 0, 'locale error: %s, %s, %s' % (language, script, country)
            return '%s_%s_%s' % (language, script, country)
        elif country is not None and len(country) > 0:
            return '%s_%s' % (language, country)
        else:
            return language

    @classmethod
    def parse(cls, locale: str):
        array = locale.split('_')
        count = len(array)
        if count == 1:
            return cls(language=array[0])
        elif count == 2:
            return cls(language=array[0], country=array[1])
        elif count == 3:
            return cls(language=array[0], script=array[1], country=array[2])
        else:
            assert False, 'locale error: %s' % locale

    @classmethod
    def from_visa(cls, visa: Visa):  # -> Optional[Locale]:
        # get from 'app.language'
        app = visa.get_property(name='app')
        if isinstance(app, dict):
            language = app.get('language')
            if language is not None and len(language) > 0:
                return Locale.parse(locale=language)
        # get from 'sys.locale'
        sys = visa.get_property(name='sys')
        if isinstance(sys, dict):
            locale = sys.get('locale')
            if locale is not None and len(locale) > 0:
                return Locale.parse(locale=locale)


class Translations:

    def __init__(self, dictionary: StringPairing):
        super().__init__()
        self.__dictionary = dictionary

    def translate(self, text: str, params: StringPairing = None) -> str:
        result = self.__dictionary.get(text)
        if result is None:
            # not found, use the text directly
            result = text
        if params is not None:
            for key, value in params.items():
                result = template_replace(template=result, key=key, value=value)
        return result

    #
    #   Factories
    #

    @classmethod
    def get(cls, locale: Union[str, Locale]):  # -> Optional[Translations]:
        if isinstance(locale, str):
            locale = Locale.parse(locale=locale)
        # check for Chinese
        script = locale.script
        if script is None:
            pass
        elif script == 'Hans':
            locale = Locale(language='zh', country='CN')
        elif script == 'Hant':
            locale = Locale(language='zh', country='TW')
        # get by full name: zh_CN
        full_name = str(locale)
        trans = cls.__get(name=full_name)
        if trans is not None:
            return trans
        # get by short name: zh
        short_name = locale.language
        if short_name != full_name:
            return cls.__get(name=short_name)

    @classmethod
    def __get(cls, name: str):  # -> Optional[Translations]:
        trans = s_translations.get(name)
        if trans is None:
            dicts = s_dictionaries.get(name)
            if dicts is not None:
                trans = Translations(dictionary=dicts)
                s_translations[name] = trans
        return trans

    @classmethod
    def set_dictionary(cls, dictionary: StringPairing, locale: Union[str, Locale]):
        if isinstance(locale, Locale):
            locale = str(locale)
        s_dictionaries[locale] = dictionary


s_dictionaries = {}  # name -> Mapping[str, str]
s_translations = {}  # name -> Translations
