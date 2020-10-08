from django import forms

class ImportFileForm(forms.Form):
    document_file = forms.FileField()