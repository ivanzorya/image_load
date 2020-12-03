from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, CreateView

from .forms import ImageForm, ChangeSizeForm
from .models import Image


class IndexView(ListView):
    model = Image
    template_name = 'index.html'


class CreateImageView(CreateView):
    model = Image
    form_class = ImageForm
    template_name = 'new_image.html'


def image_view(request, pk):
    image = get_object_or_404(Image, pk=pk)
    if request.method == "POST":
        form = ChangeSizeForm(pk=pk, data=request.POST)
        if form.is_valid():
            image = Image.objects.all()[0]
            pk = image.pk
            return redirect('get_image', pk)
        return render(
            request,
            "image.html",
            {
                "image": image,
                "form": form
            }
        )
    form = ChangeSizeForm(pk)
    return render(
        request,
        "image.html",
        {
            "image": image,
            "form": form
        }
    )
