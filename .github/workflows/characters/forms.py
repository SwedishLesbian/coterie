# characters/forms.py
from django import forms
from .models import CharacterSheet

class CharacterSheetForm(forms.ModelForm):
    class Meta:
        model = CharacterSheet
        fields = ['name', 'character_class', 'race', 'level', 'attributes']
