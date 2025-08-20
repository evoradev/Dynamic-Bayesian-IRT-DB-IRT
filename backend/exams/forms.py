from django import forms

class UploadTestForm(forms.Form):
    prova_pdf = forms.FileField(
        label='Arquivo PDF da Prova',
        help_text='Selecione o arquivo PDF contendo as questões.'
    )
    gabarito_pdf = forms.FileField(
        label='Arquivo PDF do Gabarito',
        help_text='Selecione o arquivo PDF contendo as respostas corretas.'
    )