from django.urls import path

from . import views
from .views import IndexView, CreateImageView

urlpatterns = [
    path('', IndexView.as_view(), name='index'),
    path('image/', CreateImageView.as_view(), name='add_image'),
    path('image/<int:pk>/', views.image_view, name='get_image')
]