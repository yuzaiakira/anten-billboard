from django.urls import path
from account import views

urlpatterns = [
    path('login/', views.Login.as_view(),name='login'),
    path('logout/', views.Logout.as_view(next_page='login'),name='logout'),
]
