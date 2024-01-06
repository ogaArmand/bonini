from django.contrib import admin
from .models import inscription,codepromo
# Register your models here.

class clientadmin(admin.ModelAdmin):
    list_display = ('nom','prenom','email','contact','pays','ville','estclient','estinscriptparQR','create_at','update_at')

class codepromoadmin(admin.ModelAdmin):
    list_display = ('inscription','code','estvalide','estutilise','dureevalidite','dateexpiration','create_at','update_at')

admin.site.register(inscription,clientadmin)
admin.site.register(codepromo,codepromoadmin)
