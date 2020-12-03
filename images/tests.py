import uuid

from django.core.files.uploadedfile import SimpleUploadedFile
from django.shortcuts import get_object_or_404
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from .models import Image


class ImageTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.title_1 = uuid.uuid4().hex
        self.image_1 = Image.objects.create(
            image_file=f'image/test.jpg',
            title=self.title_1
        )
        self.title_2 = uuid.uuid4().hex
        self.image_2 = Image.objects.create(
            image_file=f'image/test.jpg',
            title=self.title_2
        )

    def test_index(self):
        response_index = self.client.get(reverse('index'))
        self.assertEqual(response_index.status_code, 200)
        self.assertIn(bytes(f'{self.title_1}', encoding='UTF-8'),
                      response_index.content)
        self.assertIn(bytes(f'{self.title_2}', encoding='UTF-8'),
                      response_index.content)

    def test_new_image(self):
        response_new_image = self.client.get(reverse('add_image'))
        self.assertEqual(response_new_image.status_code, 200)
        new_title = uuid.uuid4().hex
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B'
                     )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        self.client.post(
            reverse('add_image'),
            data={'title': new_title, 'image_file': uploaded},
            follow=True
        )
        response_index = self.client.get(reverse('index'))
        self.assertIn(bytes(f'{new_title}', encoding='UTF-8'),
                      response_index.content)
        new_image = get_object_or_404(Image, title=new_title)
        response_image = self.client.get(
            reverse('get_image', args=[str(new_image.pk)])
        )
        self.assertEqual(response_image.status_code, 200)
        self.assertIn(bytes(f'{new_title}', encoding='UTF-8'),
                      response_image.content)
        images_after_file_add = Image.objects.all()
        self.assertEqual(len(images_after_file_add), 3)
        self.client.post(
            reverse('add_image'),
            data={'title': new_title, 'image_url': 'https://sun9-8.userapi.com/impf/c638528/v638528262/b999/hFdH5JkOw0E.jpg?size=271x269&quality=96&proxy=1&sign=407fa47f9776ab4b5a398f66c5934179'},
            follow=True
        )
        images_after_url_add = Image.objects.all()
        self.assertEqual(len(images_after_url_add), 4)

    def test_image(self):
        response_image_1 = self.client.get(
            reverse('get_image', args=[str(self.image_1.pk)])
        )
        self.assertEqual(response_image_1.status_code, 200)
        self.assertIn(bytes(f'{self.title_1}', encoding='UTF-8'),
                      response_image_1.content)
        response_image_2 = self.client.get(
            reverse('get_image', args=[str(self.image_2.pk)])
        )
        self.assertEqual(response_image_2.status_code, 200)
        self.assertIn(bytes(f'{self.title_2}', encoding='UTF-8'),
                      response_image_2.content)

    def test_resize(self):
        images = Image.objects.all()
        self.assertEqual(len(images), 2)
        self.client.post(reverse('get_image', args=[str(self.image_1.pk)]),
                         data={'height': 100, 'width': 100},
                         follow=True)
        old_images = Image.objects.all()
        self.assertEqual(len(old_images), len(images))
        self.client.post(reverse('get_image', args=[str(self.image_1.pk)]),
                         data={'height': 100},
                         follow=True)
        self.client.post(reverse('get_image', args=[str(self.image_2.pk)]),
                         data={'width': 100},
                         follow=True)
        new_images = Image.objects.all()
        self.assertEqual(len(new_images), 4)
