from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('Register/', signup, name='signup'),
    path('Login/', signin, name='signin'),
    path('Forgot-Password/', reset, name='reset'),
    path('Reset-Password/', change_password, name='change_password'),
    path('Vote/', vote, name='vote'),
    path("capture-face/", face_capture, name="capture_face"),
    path("train-model/", train_model, name="train_model"),
    path("capture-and-train/", capture_and_train_page, name="capture_and_train_page"),
    path('LogOut/', signout, name='signout'),
]