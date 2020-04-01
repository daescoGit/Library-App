from django.contrib import admin
from .models import Book, Magazine, BookLoan, MagazineLoan, Profile

admin.site.register(Book)
admin.site.register(Magazine)
admin.site.register(BookLoan)
admin.site.register(MagazineLoan)
admin.site.register(Profile)
