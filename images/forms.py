import requests
from PIL import Image as P_Image
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from .models import Image


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = '__all__'
        widgets = {
            'title': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 1}
            ),
            'image_url': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 1}
            )
        }

    def validate_image_url(self):
        image_formats = ("image/png", "image/jpeg", "image/jpg")
        r = requests.head(self.cleaned_data.get('image_url'))
        return r.headers["content-type"] in image_formats

    def clean(self):
        if (self.cleaned_data.get('image_file')
                and self.cleaned_data.get('image_url')):
            raise ValidationError('You should only use one of the two options:'
                                  ' "image url" or "image file"')
        elif (not self.cleaned_data.get('image_file')
                and not self.cleaned_data.get('image_url')):
            raise ValidationError('You should use one of the two options:'
                                  ' "image url" or "image file"')
        elif (self.cleaned_data.get('image_url')
              and not self.validate_image_url()):
            raise ValidationError('You should use real image url')
        return self.cleaned_data


class ChangeSizeForm(forms.Form):
    class Meta:
        model = Image

    height = forms.IntegerField(required=False)
    width = forms.IntegerField(required=False)
    widgets = {
        'height': forms.Textarea(
            attrs={'class': 'form-control', 'rows': 1}
        ),
        'width': forms.Textarea(
            attrs={'class': 'form-control', 'rows': 1}
        )
    }

    def __init__(self, pk, *args, **kwargs):
        super(ChangeSizeForm, self).__init__(*args, **kwargs)
        self.pk = pk

    def check_new_size(self, new_width, new_height, p_image_size):
        old = new_width / new_height
        new = p_image_size[0] / p_image_size[1]
        return old == new

    def clean(self, *args, **kwargs):
        image = get_object_or_404(Image, pk=self.pk)
        new_image = image.image_file
        p_image = P_Image.open(new_image)
        new_width = self.cleaned_data.get('width')
        new_height = self.cleaned_data.get('height')
        if new_width and new_height:
            if not self.check_new_size(new_width, new_height, p_image.size):
                raise ValidationError('''You can't change the aspect ratio''')
        self.pk = Image.resize_image(image, p_image, new_width, new_height)
        return self.cleaned_data
