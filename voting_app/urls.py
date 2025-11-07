from django.urls import path
from .views import *
urlpatterns = [
    path('', home, name='home'),
    path('Register/', signup, name='signup'),
    path('Login/', signin, name='signin'),
    path('Forgot-Password/', reset, name='reset'),
    path('Reset-Password/', change_password, name='change_password'),
    path('vote/<int:user_id>/', vote, name='vote'),
    path('capture/', capture_and_train_page, name='capture_and_train_page'),
    path('capture-face/', capture_face, name='capture_face'),
    path('train-model/', train_model, name='train_model'),
    path('face_recognition/', face_recognition_view, name='face_recognition'),
    path('election_results/', election_results, name='election_results'),
    path('LogOut/', signout, name='signout'),
]