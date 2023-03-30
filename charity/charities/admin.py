from django.contrib import admin
from charities.models import Benefactor, Charity, Task


@admin.register(Benefactor)
class BenafactorAdmin(admin.ModelAdmin):
    pass



