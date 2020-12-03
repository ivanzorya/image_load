import uuid

import requests
from django.db import models
from django.urls import reverse


class Image(models.Model):
    title = models.TextField()
    image_file = models.ImageField(blank=True, upload_to='image/')
    image_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["-pk"]

    def save(self, *args, **kwargs):
        if self.image_url:
            response = requests.get(str(self.image_url))
            name = uuid.uuid4().hex
            extension = None
            extensions = [
                'jpg', 'jpeg', 'jfif', 'png', 'tif', 'tiff', 'gif', 'bmp'
            ]
            for i in extensions:
                if i in self.image_url:
                    extension = i
                    break
            file = open(f"media/image/{name}.{extension}", "wb")
            file.write(response.content)
            file.close()
            Image.objects.create(
                image_file=f"image/{name}.{extension}",
                title=self.title
            )
        elif self.image_file:
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        if self.pk:
            return reverse('get_image', args=[str(self.pk)])
        else:
            image = Image.objects.filter(title=self.title)[0]
            return reverse('get_image', args=[str(image.pk)])

    def resize_image(self, p_image, new_width, new_height):
        extension = p_image.format
        if not new_width:
            new_width = p_image.width * new_height / p_image.height
        elif not new_height:
            new_height = p_image.height * new_width / p_image.width
        new_title = ' '.join([
            str(self.title), str(int(new_width)), str(int(new_height))
        ])
        new_size = p_image.resize((int(new_width), int(new_height)))
        name = uuid.uuid4().hex
        new_size.save(f"media/image/{name}.{extension}")
        Image.objects.create(
            image_file=f"image/{name}.{extension}",
            title=new_title)
