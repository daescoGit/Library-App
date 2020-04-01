from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Book, Magazine, BookLoan, MagazineLoan, Profile


@login_required(login_url='/users/login/')
def index(request):
    if request.user.is_staff:
        return redirect(reverse('library_app:overdue'))
    book_loans = BookLoan.objects.filter(user__user__username=request.user)
    magazine_loans = MagazineLoan.objects.filter(user__user__username=request.user)
    books = Book.objects.all()
    magazines = Magazine.objects.all()

    context = {
        'book_loans': book_loans,
        'magazine_loans': magazine_loans,
        'books': books,
        'magazines': magazines
    }
    return render(request, 'library_app/index.html', context)


@login_required(login_url='/users/login/')
def overdue(request):
    if not request.user.is_staff:
        return redirect(reverse('library_app:index'))
    book_loans = BookLoan.objects.filter(overdue=True)
    magazine_loans = MagazineLoan.objects.filter(overdue=True)
    context = {
        'book_loans': book_loans,
        'magazine_loans': magazine_loans
    }
    return render(request, 'library_app/overdue.html', context)


@login_required(login_url='/users/login/')
def return_book(request):
    if request.method == 'POST' and "return-book" in request.POST:
        pk = request.POST["return-book"]
        loan = get_object_or_404(BookLoan, pk=pk)
        loan.delete()
    return redirect(reverse('library_app:index'))


@login_required(login_url='/users/login/')
def return_magazine(request):
    if request.method == 'POST' and "return-magazine" in request.POST:
        pk = request.POST["return-magazine"]
        loan = get_object_or_404(MagazineLoan, pk=pk)
        loan.delete()
    return redirect(reverse('library_app:index'))


@login_required(login_url='/users/login/')
def loan_book(request):
    if request.method == 'POST' and "loan-book" in request.POST:
        user = get_object_or_404(Profile, user__username=request.user)
        overdues = BookLoan.objects.filter(user__user__username=request.user).filter(overdue=True)
        if user.book_loans.count() > 9 or overdues:
            print('Active book loans reached or one or more loans are overdue !')
            return redirect(reverse('library_app:index'))
        else:
            pk = request.POST["loan-book"]
            loan = BookLoan()
            loan.book = get_object_or_404(Book, pk=pk)
            loan.user = user
            loan.save()
            return redirect(reverse('library_app:index'))


@login_required(login_url='/users/login/')
def loan_magazine(request):
    if request.method == 'POST' and "loan-magazine" in request.POST:
        user = get_object_or_404(Profile, user__username=request.user)
        overdues = MagazineLoan.objects.filter(user__user__username=request.user).filter(overdue=True)
        if user.magazine_loans.count() > 2 or overdues:
            print('Active book loans reached or one or more loans are overdue !')
            return redirect(reverse('library_app:index'))
        else:
            pk = request.POST["loan-magazine"]
            loan = MagazineLoan()
            loan.magazine = get_object_or_404(Magazine, pk=pk)
            loan.user = user
            loan.save()
            return redirect(reverse('library_app:index'))
