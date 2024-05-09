from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth.views import LoginView
import datetime
from django.views.generic import *
from django.views import View
from django.contrib.auth.models import auth
from django.urls import reverse_lazy, reverse
from django.contrib.auth.forms import UserCreationForm
from django import forms

logging.basicConfig(level=logging.INFO, filename='logging.log', filemode='a', format='%(asctime)s %(levelname)s %(message)s')

def home(request):
    latest_article = News.objects.latest('date')
    return render(request, 'home.html', {'latest_article': latest_article})

def about_company(request):
    info = CompanyInfo.objects.first()
    return render(request, 'about.html', {'company_info': info})

def news(request):
    news = News.objects.all().order_by('-date')
    return render(request, 'news.html', {'news': news})

def promocodes(request):
    promocodes = Promocode.objects.all()
    return render(request, 'promocodes.html', {'promocodes': promocodes})

def faqs(request):
    faqs = FAQ.objects.all()
    return render(request, 'faqs.html', {'faqs': faqs})

def contacts(request):
    contacts = Contact.objects.all()
    return render(request, 'contacts.html', {'contacts': contacts})

def vacancies(request):
    vacancies = Vacancy.objects.all()
    return render(request, 'vacancies.html', {'vacancies': vacancies})

def reviews(request):
    reviews = Review.objects.all()
    return render(request, 'reviews.html', {'reviews': reviews})

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=5)
    class Meta:
        model = Review
        fields = ['title', 'rating','text']

class ReviewCreateView(View):
    def get(self, request, **kwargs):
        if request.user.is_authenticated and request.user.status == 'client':

            logging.info(f"{request.user.username} called ReviewCreateView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")

            form = ReviewForm()
            return render(request, 'review_create_form.html', {'form': form})
        return redirect('login')

    def post(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == 'client':
            form = ReviewForm(request.POST)
            if form.is_valid():
                logging.info(f"ReviewForm has no errors)")

                title = form.cleaned_data['title']
                rating = form.cleaned_data['rating']
                text = form.cleaned_data['text']

                review = Review.objects.create(title=title, rating=rating, text=text, user=request.user)
                logging.info(f"Review '{review.title}' was created by {request.user.username} ")
                return redirect('reviews')
        logging.warning("User is not authenticated")
        return redirect('login')


def privacy_policy(request):
    return render(request, 'privacy.html')


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'age', 'phone', 'address', 'password1', 'password2']

class UserRegistrationView(CreateView):
    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logging.info("Registration form has no errors")
            user = form.save(commit=False)
            user.save()

            logging.info(f"{user.username} REGISTER (status: {user.status}) | user's Timezone: {request.user.timezone}")
            return redirect('login')
        else:
            logging.warning("Registration form is invalid")
            return render(request, 'registration.html', {'form': form})

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})

class UserLoginView(LoginView):
    redirect_authenticated_user = True
    template_name = 'login.html'
    def get_success_url(self):  
        logging.info("User LOGIN")
        return reverse_lazy('home')
            
class UserLogoutView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            logging.info(f"{request.user.username} LOGOUT (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            auth.logout(request)
        return redirect('home')


class MedicinesListView(View):
    model = Medicines
    #context_object_name = 'medicine_list'
    queryset = Medicines.objects.all()

    def get(self, request, *args, **kwargs):
        min_cost = request.GET.get('min_cost')
        max_cost = request.GET.get('max_cost')
        medics = self.filter_medic(min_cost, max_cost)
        data_list = []
        for medic in medics:
            data_list.append({
                'id': medic.id,
                'name': medic.name,
                'cost': medic.cost,
            })
        return render(request, "medicines_list.html", {'medicines': data_list})

    @staticmethod
    def filter_medic(min=None, max=None):
        medic = Medicines.objects.all()

        filtered = None

        if min is not None and max is not None:
            filtered = medic.filter(cost__gte=min, cost__lte=max)
        elif min is not None:
            filtered = medic.filter(cost__gte=min)
        elif max is not None:
            filtered = medic.filter(cost__lte=max)

        if filtered is not None:
            return filtered
        return medic


class MedicinesDetailView(View):
    model = Medicines
    def get(self, request, *args, **kwargs):
        medic = get_object_or_404(Medicines, pk=self.kwargs['pk'])        
        data_list = []
        data_list.append({
            'id': medic.id,
            'name': medic.name,
            'code': medic.code,
            'instructions': medic.instructions,
            'description': medic.description,
            'cost': medic.cost,
            'photo': medic.photo,
            'categories': medic.categories,
            'suppliers': medic.suppliers
        })
        return render(request, "medicine_detail.html", {'medicine': medic})
