from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.contrib.auth.views import LoginView
import datetime
import requests
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
    rating = forms.IntegerField(label='Ацэнка', min_value=1, max_value=5)
    class Meta:
        model = Review
        fields = ['title', 'rating','text']
        labels = {
            'title': 'Тэма',
            'rating': 'Ацэнка',
            'text': 'Тэкст',
        }

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

class ReviewEditView(View):
    def get(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            form = ReviewForm(instance=review)
            return render(request, 'review_edit.html', {'form': form, 'review': review})
        return redirect('login')

    def post(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                form.save()
                return redirect('reviews')
        return render(request, 'review_edit.html', {'form': form, 'review': review})

class ReviewDeleteView(View):
    def get(self, request, review_id, *args, **kwargs):
        review = get_object_or_404(Review, id=review_id)
        if request.user.is_authenticated and review.user == request.user:
            review.delete()
        return redirect('reviews')

def privacy_policy(request):
    return render(request, 'privacy.html')



class RegistrationForm(UserCreationForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Паўтарыце пароль', widget=forms.PasswordInput)

    class Meta:
        model = User
        
        fields = ['username', 'first_name', 'last_name', 'age', 'phone', 'address', 'password1', 'password2']
        labels = {
            'username': 'Імя карыстальніка',
            'first_name': 'Імя',
            'last_name': 'Прозвішча',
            'age': 'Узрост',
            'phone': 'Тэлефон', 
            'address': 'Адрас',
            'password1': 'Пароль',
            'password2': 'Паўтарыце пароль',
        }


class UserRegistrationView(CreateView):

    def get(self, request, *args, **kwargs):
        form = RegistrationForm()
        return render(request, 'registration.html', {'form': form})

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            logging.info("Registration form has no errors")
            user = form.save(commit=False)
            user.save()

            if request.user.is_authenticated:
                user.timezone = request.user.timezone
            else:
                user.timezone = get_localzone_name()
                        
            user.save()

            logging.info(f"{user.username} REGISTER (status: {user.status}) | user's Timezone: {user.timezone}")
            return redirect('login')
        else:
            logging.warning("Registration form is invalid")
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
        no_results = False

        min_cost = request.GET.get('min_cost')
        if not min_cost:
            min_cost = 0
        max_cost = request.GET.get('max_cost')
        if not max_cost:
            max_cost = 1000

        search_query = request.GET.get('search')

        
        medics = self.filter_medic(min_cost, max_cost)


        if search_query:
            medics = medics.filter(name__icontains=search_query)
            if not medics:
                no_results = True
        else:
            medics = self.filter_medic(min_cost, max_cost)

        medics = medics.order_by('name')

        data_list = []
        for medic in medics:
            data_list.append({
                'id': medic.id,
                'name': medic.name,
                'cost': medic.cost,
            })
        return render(request, "medicines_list.html", {'medicines': data_list, 'no_results': no_results})

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
        departments = DepartmentMedicine.objects.filter(medicine=medic)
        suppliers = medic.suppliers
        context = {
            'medicine': medic,
            'departments': departments,
            'suppliers': suppliers,
        }
        return render(request, "medicine_detail.html", context)

class CatigoriesListView(View):
    model = Categories

    def get(self, request, *args, **kwargs):
        type_med = Categories.objects.all()
        return render(request, "medicine_categories.html", {'categories': type_med})
    
class OrderForm(forms.Form):
    amount = forms.IntegerField(min_value=1)
    
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label="Выберыце аддзяленне")
    promocode = forms.CharField(max_length=10, required=False)

class OrderCreateView(View):
    def get(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "client" and Medicines.objects.filter(pk=pk).exists():
            logging.info(f"{request.user.username} called OrderCreateView | user's Timezone: {request.user.timezone}")
            medic = Medicines.objects.get(pk=pk)
            form = OrderForm()     
            return render(request, 'order_create_form.html', {'form': form, 'medic': medic})
        
        logging.error(f"Call failed OrderCreateView")
        return HttpResponseNotFound('Страніца не знойдзена')
    
    def post(self, request, pk, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "client":
            medic = Medicines.objects.get(pk=pk)
            form = OrderForm(request.POST)
            if form.is_valid():
                logging.info(f"OrderForm has no errors")

                amount = form.cleaned_data['amount']
                department = form.cleaned_data['department']
                code = form.cleaned_data['promocode']

                department_medicine = get_object_or_404(DepartmentMedicine, department_id=department, medicine_id=medic)
                quantity = department_medicine.quantity

                promocode = Promocode.objects.filter(code=code).first()

                if amount > quantity:
                     logging.warning(f"{amount} is greater than {quantity}")
                     return HttpResponse("Выберыце іншае аддзяленне аптэкі або дачакайцеся новай пастаўкі")
                
                sale = Sale.objects.create(
                    user=request.user,
                    department=department,
                    medicine=medic,
                    quantity=amount,
                    promocode=promocode,
                    price=medic.cost * amount,
                    price_prom=medic.cost * amount
                ) 
                department_medicine.quantity -= amount
                department_medicine.save()
                if promocode:
                    logging.info(f"Promocode {promocode.code} used by {request.user.username}")
                    sale.use_discount(promocode)

                url = reverse('user_order', kwargs={"pk": sale.user_id, "jk": sale.id})
                return redirect(url)
                            
        elif request.user.is_authenticated and request.user.status == "staff":
            logging.error(f"{request.user.username} has status {request.user.status}")
            return HttpResponseNotFound("Толькі для кліентаў")
        else:
            logging.error(f"User is not authenticated")
            return HttpResponse('Увайдзіце ў акаўнт, каб зрабіць заказ')

class UserOrderView(View):
    def get(self, request, pk, jk, *args, **kwargs):
        if request.user.is_authenticated and request.user.id==int(pk) and Sale.objects.filter(user_id=int(pk), id=int(jk)).exists():
            logging.info(f"{request.user.username} called SpecificOrderView | user's Timezone: {request.user.timezone}")

            order = Sale.objects.filter(user_id=pk, id=jk).first()

            return render(request, 'order_detail.html', {'order': order})
        return HttpResponseNotFound("Страніца не знойдзена")

class UserOrdersListView(View):
    def get(self, request, pk, *args, **kwargs):

        if request.user.is_authenticated and request.user.id==int(pk):
            logging.info(f"{request.user.username} called UserOrderView | user's Timezone: {request.user.timezone}")
            order = Sale.objects.filter(user_id=pk)
            return render(request, "orders_list.html", {'orders': order})

        logging.error(f"Call failed UserOrderView")
        return HttpResponseNotFound("Страніца не знойдзена")

class DepartmentInfo(View):
    model = Department

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "client":
            logging.info(f"{request.user.username} called DepartmentInfo | user's Timezone: {request.user.timezone}")
            points = Department.objects.all()
            return render(request, "department_info.html", {'points': points})
        logging.error(f"Call failed DepartmentInfo")
        return HttpResponseNotFound('Страніца не знойдзена')

class OrderListView(View):
    def get(self, request, *args, **kwargs):      
        if request.user.is_authenticated and request.user.status == "staff":

            logging.info(f"{request.user.username} called OrderListView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            sales = Sale.objects.all()
            total_revenue = sum(sale.price for sale in sales)

            revenue_by_department = {}
            for sale in sales:
                department_name = sale.department.no
                revenue_by_department[department_name] = revenue_by_department.get(department_name, 0) + sale.price
            return render(request, 
                        'staff_order.html', {
                        'sales': sales,
                        'total_revenue': total_revenue,
                        'revenue_by_department': revenue_by_department
                        })
            #return render(request, "staff_order.html", {'sales': sales})


        logging.error(f"{request.user.username} has status {request.user.status}") 
        return HttpResponseNotFound("Страніца не знойдзена")
    
class SupplierListView(View):  
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.status == "staff":
            logging.info(f"{request.user.username} called SupplierListView (status: {request.user.status}) | user's Timezone: {request.user.timezone}")
            suppliers = Supplier.objects.all().prefetch_related('supply__medicine')
            return render(request, "suppliers.html", {'suppliers': suppliers})
        logging.error(f"{request.user.username} tried to call SupplierListView (status: {request.user.status})")
        return HttpResponseNotFound("Толькі для персаналу")    

#API
# class MedicalFactsView(View):
#     def get(self, request):
#         # URL запроса к OpenFDA API
#         url = 'https://api.fda.gov/drug/label.json?limit=5'

#         # Отправка запроса к OpenFDA API
#         response = requests.get(url)

#         # Проверка успешности запроса и обработка данных
#         if response.status_code == 200:
#             data = response.json()
#             # Получение фактов из ответа
#             facts = []
#             if 'results' in data and data['results']:
#                 for result in data['results']:
#                     fact = result.get('description', '')
#                     if fact:
#                         facts.append(fact)
#             return JsonResponse({'facts': facts})
#         else:
#             return JsonResponse({'error': 'Failed to fetch data from API'}, status=500)

class MedicalFactsView(View):
    def get(self, request):
        if request.user.is_authenticated:
            url = 'https://api.fda.gov/drug/label.json?limit=5'

            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()
                
                
                facts = []
                if 'results' in data and data['results']:
                    for result in data['results']:
                        fact = result.get('description', '')
                        if fact:
                            facts.append(fact)
                return render(request, 'medical_facts.html', {'facts': facts})
            else:
                return render(request, 'medical_facts.html', {'error': 'Failed to fetch data from API'})
        return HttpResponseNotFound("Page not found")
        

# class RxNormAPI:
#     BASE_URL = 'https://rxnav.nlm.nih.gov/REST'

#     @classmethod
#     def get_concepts(cls, search_term):
#         url = f'{cls.BASE_URL}/rxcui.json?name={search_term}'
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             return data.get('idGroup', {}).get('rxnormId', [])
#         else:
#             return []

#     @classmethod
#     def get_rxcui_properties(cls, rxcui):
#         url = f'{cls.BASE_URL}/rxcui/{rxcui}/properties.json'
#         response = requests.get(url)
#         if response.status_code == 200:
#             data = response.json()
#             properties = data.get('properties', {})
#             active_ingredients = properties.get('activeMoiety', [])
#             return active_ingredients
#         else:
#             return []

# class RxView(View):
#     def get(self, request):
#         search_term = request.GET.get('search', '')
#         concepts = RxNormAPI.get_concepts(search_term)
#         active_ingredients = []
#         for concept in concepts:
#             ingredients = RxNormAPI.get_rxcui_properties(concept)
#             print(f"Ingredients for concept {concept}: {ingredients}")
#             active_ingredients.extend(ingredients)
#         print(f"Active ingredients: {active_ingredients}")
#         return render(request, 'rx_code.html', {'active_ingredients': active_ingredients, 'concepts': concepts})

class RxNormAPI:
    BASE_URL = 'https://rxnav.nlm.nih.gov/REST'

    @classmethod
    def get_concepts(cls, search_term):
        url = f'{cls.BASE_URL}/rxcui.json?name={search_term}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('idGroup', {}).get('rxnormId', [])
        else:
            return []

    @classmethod
    def get_rxcui_properties(cls, rxcui):
        url = f'{cls.BASE_URL}/rxcui/{rxcui}/properties.json'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            properties = data.get('properties', {})
            # Извлекаем название и активные ингредиенты (если доступны)
            info = {
                'name': properties.get('name', 'N/A'),
                'synonym': properties.get('synonym', 'N/A'),
                'tty': properties.get('tty', 'N/A'),
                'language': properties.get('language', 'N/A'),
                'suppress': properties.get('suppress', 'N/A'),
                'umlscui': properties.get('umlscui', 'N/A')
            }
            return info
        else:
            return {}

class RxView(View):
    def get(self, request):
        if request.user.is_authenticated:
            search_term = request.GET.get('search', '')
            concepts = RxNormAPI.get_concepts(search_term)
            concept_info = []

            for concept in concepts:
                concept_data = {
                    'rxcui': concept,
                    'properties': RxNormAPI.get_rxcui_properties(concept)
                }
                concept_info.append(concept_data)

            return render(request, 'rx_code.html', {'concept_info': concept_info})
        return HttpResponseNotFound("Page not found")