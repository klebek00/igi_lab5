import base64
from datetime import datetime
import io
from urllib import parse

from django.http import HttpResponseNotFound
import numpy as np
from statistics import median, mode, mean
import matplotlib
from django.db.models import Sum, Count, Avg

from .models import *
from matplotlib import pyplot as plt
from django.shortcuts import render

def clients(request): 
    if request.user.is_authenticated and request.user.is_superuser:   
        clients = User.objects.filter(status='client').order_by('first_name')
        ages = []
        for client in clients:
            ages.append(client.age)

        average_age = round(mean(ages), 2)
        median_age = round(median(ages), 2)

        return render(request, 'clients_stat.html', {'clients': clients,
                                                'average_age': average_age,
                                                'median_age': median_age,
                                                })
    return HttpResponseNotFound("Page not found")


def medicine(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        medics = Medicines.objects.all().order_by('name')
        
        medic_orders = Sale.objects.values('medicine__name').annotate(order_count=Count('medicine__name')).order_by('-order_count')
        most_popular = medic_orders.first()

        return render(request, 'medic_stat.html', {'medics': medics,
                                                'most_popular': most_popular,
                                                })
    
    return HttpResponseNotFound("Page not found")


def sales(request):
    if request.user.is_authenticated and request.user.is_superuser: 
        orders = Sale.objects.filter(is_canceled=False)
        prices = []
        general_sales = 0.0
        for order in orders:
            prices.append(order.price_prom)
            general_sales += order.price_prom
    
        average_sales = round(mean(prices), 2)
        median_sales = round(median(prices), 2)
        mode_sales = round(mode(prices), 2)

        url, yearly_sales_data = linear_sales_trend()
        image_urls = year_sales_volume()

        return render(request, 'sale_stat.html', {'general_sales': general_sales,
                                                'average_sales': average_sales,
                                                'median_sales': median_sales,
                                                'mode_sales': mode_sales,
                                                'image': url, 
                                                'yearly_sales_data': yearly_sales_data,
                                                'image_urls': image_urls,
                                                })
    return HttpResponseNotFound("Page not found")


def yearly_sales_report(year):
    orders = Sale.objects.filter(date__year=year, is_canceled=False)
    total_sales_for_year = orders.aggregate(total_sales=Sum('price_prom'))['total_sales'] or 0
    return total_sales_for_year


def yearly_sales_trend():
    current_year = datetime.now().year
    last_three_years = range(current_year - 2, current_year + 1)
    yearly_sales_ = []

    for year in last_three_years:
        sales = yearly_sales_report(year)
        yearly_sales_.append(round(sales, 2))

    return list(last_three_years), yearly_sales_


def linear_sales_trend():

    matplotlib.use('Agg')

    years, sales = yearly_sales_trend()

    plt.figure(figsize=(14, 6))

    plt.plot(years, sales, color='yellowgreen', marker='o', linestyle='-')
    plt.xlabel('Год')
    plt.ylabel('Агульная перавага, руб')
    plt.title('Продажы за год')
    plt.xticks(years)
    plt.grid(True)


    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    url = parse.quote(string)

    yearly_sales_data = list(zip(years, sales))

    return url, yearly_sales_data


def year_sales_volume():
    matplotlib.use('Agg')

    years, sales = yearly_sales_trend()

    image_urls = []

    colors = ['yellowgreen', 'yellowgreen', 'yellowgreen']

    plt.figure(figsize=(10, 10))

    plt.bar(years, sales, color=colors)
    plt.xlabel('Год')
    plt.ylabel('Продажы, руб')
    plt.xticks(years)
    plt.title(f'Продажы за год - {years}')

    fig = plt.gcf()
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    url = parse.quote(string)

    image_urls.append(url)

    return image_urls


def class_diagramm(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return render(request, 'diagram.html')
    return HttpResponseNotFound("Page not found")

def department_revenue_chart(request):
    if request.user.is_authenticated and request.user.is_superuser: 

        current_year = datetime.now().year
        departments = Department.objects.all()
        data = {}

        for department in departments:
            sales = Sale.objects.filter(department=department, date__year=current_year, is_canceled=False)
            revenue = sales.aggregate(total_revenue=Sum('price'))['total_revenue'] or 0
            data[department.no] = revenue

        labels = data.keys()
        values = data.values()

        plt.bar(labels, values, color = 'yellowgreen')
        plt.xlabel('Аддзялення')
        plt.ylabel('Перавага')
        plt.title(f'Перавага у {current_year} годзе')
        plt.xticks(rotation=45)
        plt.tight_layout()

        fig = plt.gcf()
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        url = parse.quote(string)

        return render(request, 'revenue_chart.html', {'image': url})