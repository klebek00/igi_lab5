from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(Categories)
admin.site.register(Supplier)
admin.site.register(Supply)
admin.site.register(Medicines)
admin.site.register(Department)
admin.site.register(Sale)
admin.site.register(SaleItem)
admin.site.register(Promocode)
admin.site.register(UsedDiscounts)

admin.site.register(News)
admin.site.register(CompanyInfo)
admin.site.register(FAQ)
admin.site.register(Contact)
admin.site.register(Vacancy)
admin.site.register(Review)
