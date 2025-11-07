from django.urls import path
from .views import *

urlpatterns = [
    path('', admin_login, name='admin_login'),
    path('logout/', admin_logout, name='admin_logout'),
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('add_candidate/', add_candidate, name='add_candidate'),
    path('edit-candidate/<int:candidate_id>/', edit_candidate, name='edit_candidate'),
    path('delete-candidate/<int:candidate_id>/', delete_candidate, name='delete_candidate'),
    path('view_candidates/', view_candidates, name='view_candidates'),
    path('view-voters/', view_voters, name='view_voters'),
    path('results/', view_votes, name='results'),

]