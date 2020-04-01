from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.title}"


class Magazine(models.Model):
    title = models.CharField(max_length=100)
    issue = models.SmallIntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.title}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    book_loans = models.ManyToManyField(Book, through='BookLoan')
    magazine_loans = models.ManyToManyField(Magazine, through='MagazineLoan')

    def __str__(self):
        return f"{self.user}"


class BookLoan(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    overdue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.book} - {self.date.strftime('%d-%m-%Y %H:%M:%S')} - overdue: {self.overdue}"

    def remaining_days(self):
        days = (date.today()-self.date.date()).days
        if days > 30:
            self.overdue = True
            self.save()
            return f"{days - 30} days overdue"
        return f"{30 - days} days remaining"


class MagazineLoan(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    magazine = models.ForeignKey(Magazine, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    overdue = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.magazine} - {self.date.strftime('%d-%m-%Y %H:%M:%S')}"

    def remaining_days(self):
        days = (date.today()-self.date.date()).days
        if days > 7:
            self.overdue = True
            self.save()
            return f"{days - 7} days overdue"
        return f"{7 - days} days remaining"


# extending User
# signal - hooking the create_user_profile and save_user_profile methods to the User model on save
# single db query - users = User.objects.all().select_related('profile')
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


# fat model approach
# alt: put in model?/better solution?, why in view /w different end points?, make more dry?
# todo fix refresh bug (form resubmission, redirect)
def action_response(request):
    user = get_object_or_404(Profile, user__username=request.user)

    if request.method == 'POST' and "loan-book" in request.POST:
        overdues = BookLoan.objects.filter(user__user__username=request.user).filter(overdue=True)
        if user.book_loans.count() > 9 or overdues:
            return 'Active book loans reached or one or more loans are overdue !'
        else:
            pk = request.POST["loan-book"]
            loan = BookLoan()
            loan.book = get_object_or_404(Book, pk=pk)
            loan.user = user
            loan.save()
            return f"Checked out book: {loan.book}"

    if request.method == 'POST' and "return-book" in request.POST:
        pk = request.POST["return-book"]
        loan = get_object_or_404(BookLoan, pk=pk)
        loan.delete()
        return f"Checked in book: {loan.book}"

    if request.method == 'POST' and "loan-magazine" in request.POST:
        overdues = MagazineLoan.objects.filter(user__user__username=request.user).filter(overdue=True)
        if user.magazine_loans.count() > 2 or overdues:
            return 'Active magazine loans reached or one or more loans are overdue !'
        else:
            pk = request.POST["loan-magazine"]
            loan = MagazineLoan()
            loan.magazine = get_object_or_404(Magazine, pk=pk)
            loan.user = user
            loan.save()
            return f"Checked out magazine: {loan.magazine}"

    if request.method == 'POST' and "return-magazine" in request.POST:
        pk = request.POST["return-magazine"]
        loan = get_object_or_404(MagazineLoan, pk=pk)
        loan.delete()
        return f"Checked in magazine: {loan.magazine}"
