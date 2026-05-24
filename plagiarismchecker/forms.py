from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class StyledFormMixin:
    def _apply_classes(self):
        for name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            base = 'form-control'
            if isinstance(widget, (forms.ClearableFileInput, forms.FileInput)):
                base = 'form-control'
            elif isinstance(widget, forms.Textarea):
                base = 'form-control'
            widget.attrs['class'] = (existing + ' ' + base).strip()
            widget.attrs.setdefault('placeholder', field.label)


class CheckTextForm(forms.Form, StyledFormMixin):
    q = forms.CharField(label='Text to analyze', widget=forms.Textarea(attrs={'rows': 10, 'placeholder': 'Paste your text here...'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_classes()


class UploadDocumentForm(forms.Form, StyledFormMixin):
    docfile = forms.FileField(label='Choose a TXT, DOCX, or PDF file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_classes()


class CompareTextForm(forms.Form, StyledFormMixin):
    q1 = forms.CharField(label='Text 1', widget=forms.Textarea(attrs={'rows': 8}))
    q2 = forms.CharField(label='Text 2', widget=forms.Textarea(attrs={'rows': 8}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_classes()


class CompareFilesForm(forms.Form, StyledFormMixin):
    docfile1 = forms.FileField(label='First file')
    docfile2 = forms.FileField(label='Second file')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_classes()


class StyledUserCreationForm(UserCreationForm, StyledFormMixin):
    email = forms.EmailField(required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_classes()
        self.fields['username'].widget.attrs['placeholder'] = 'Username'
        self.fields['email'].widget.attrs['placeholder'] = 'Email address'
        self.fields['password1'].widget.attrs['placeholder'] = 'Password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

class TextForm(forms.Form):

    text = forms.CharField(

        widget=forms.Textarea(attrs={

            'class': 'form-control',

            'rows': 10,

            'placeholder': 'Paste text here...'

        }),

        label='Text to analyze'
    )

class UploadFileForm(forms.Form):

    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                'class': 'form-control'
            }
        )
    )