# -*- coding: utf-8 -*-

from babel import Locale

from phonenumbers.data import _COUNTRY_CODE_TO_REGION_CODE

from django.conf import settings
from django.utils import translation
from django.forms import Select, TextInput
from django.forms.widgets import MultiWidget

from phonenumber_field.phonenumber import PhoneNumber


class PhonePrefixSelect(Select):

    initial = None

    def __init__(self, initial=None):
        choices = [('', '---------')]
        locale = Locale(translation.to_locale(translation.get_language()))
        for prefix, values in _COUNTRY_CODE_TO_REGION_CODE.iteritems():
            prefix = '+%d' % prefix
            if initial and initial in values:
                self.initial = prefix
            for country_code in values:
                country_name = locale.territories.get(country_code)
                if country_name:
                    choices.append((prefix, u'%s %s' % (country_name, prefix)))
        return super(PhonePrefixSelect, self).__init__(
            choices=sorted(choices, key=lambda item: item[1]))

    def render(self, name, value, *args, **kwargs):
        return super(PhonePrefixSelect, self).render(
            name, value or self.initial, *args, **kwargs)


class PhoneNumberPrefixWidget(MultiWidget):
    """
    A Widget that splits phone number input into:
    - a country select box for phone prefix
    - an input for local phone number
    """
    def __init__(self, attrs=None, initial=None):
        initial = initial or getattr(settings, 'PHONENUMBER_DEFAULT_PREFIX', None)
        widgets = (PhonePrefixSelect(initial), TextInput(),)
        super(PhoneNumberPrefixWidget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            if isinstance(value, basestring):
                try:
                    value = PhoneNumber.from_string(value)
                except:
                    pass
            if type(value) == PhoneNumber:
                if value.country_code and value.national_number:
                    return ["+%d" % value.country_code, value.national_number]
        return [None, None]

    def value_from_datadict(self, data, files, name):
        values = super(PhoneNumberPrefixWidget, self).value_from_datadict(
            data, files, name)
        if not all(values):
            values = ['', '']
        return '%s%s' % tuple(values)
