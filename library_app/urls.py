from django.urls import path
from . import views

app_name = 'library_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('overdue/', views.overdue, name='overdue'),
    path('return_book/', views.return_book, name='return_book'),
    path('return_magazine/', views.return_magazine, name='return_magazine'),
    path('loan_book/', views.loan_book, name='loan_book'),
    path('loan_magazine/', views.loan_magazine, name='loan_magazine')
]
