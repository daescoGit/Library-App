from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Book, Magazine, BookLoan, MagazineLoan, Profile, action_response


@login_required(login_url='/users/login/')
def index(request):
    if request.user.is_staff:
        return HttpResponseRedirect(reverse('library_app:overdue'))
    book_loans = BookLoan.objects.filter(user__user__username=request.user)
    magazine_loans = MagazineLoan.objects.filter(user__user__username=request.user)
    books = Book.objects.all()
    magazines = Magazine.objects.all()

    context = {
        'book_loans': book_loans,
        'magazine_loans': magazine_loans,
        'books': books,
        'magazines': magazines,
        'action_res': action_response(request)
    }
    return render(request, 'library_app/index.html', context)


@login_required(login_url='/users/login/')
def overdue(request):
    if not request.user.is_staff:
        return HttpResponseRedirect(reverse('library_app:index'))
    book_loans = BookLoan.objects.filter(overdue=True)
    magazine_loans = MagazineLoan.objects.filter(overdue=True)
    context = {
        'book_loans': book_loans,
        'magazine_loans': magazine_loans
    }
    return render(request, 'library_app/overdue.html', context)
