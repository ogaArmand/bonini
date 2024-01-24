from django.contrib import admin
from .models import inscription,codepromo,lemenu,typemenu,stade,commande,commande_detail,niveaumatch,listematch,commende_match
from .models import Location,menu_stade,menu_restaurant,Gallerie
from mptt.admin import TreeRelatedFieldListFilter
from mptt.admin import DraggableMPTTAdmin
from django.utils.safestring import mark_safe
# Register your models here.

class clientadmin(admin.ModelAdmin):
    list_display = ('stade','nom','prenom','email','contact','pays','ville','estclient','estinscriptparQR','create_at','update_at')


class codepromoadmin(admin.ModelAdmin):
    list_display = ('inscription','code','estvalide','estutilise','dureevalidite','dateexpiration','create_at','update_at')

class menuadmin(admin.ModelAdmin):
    list_display = ('libelle','typemenu','prix','reduction','prixpromo','estactif','image')

class typemenuadmin(admin.ModelAdmin):
    list_display = ('libelle','image')

class stadeAdmin(DraggableMPTTAdmin):
    list_display = ('tree_actions', 'indented_title', 'name')
    list_display_links = ('indented_title',)
    list_filter = (
        ('parent', TreeRelatedFieldListFilter),
    )

    def indented_title(self, obj):
        return mark_safe(
            '<div style="text-indent:{}px">{}</div>'.format(
                obj._mpttfield('level') * 20,
                obj.name,
            )
        )

    indented_title.short_description = 'stade'

class commandeadmin(admin.ModelAdmin):
    list_display = ('inscription','codepromo','ref','quantite','prixtotal','nbarticle','estfacture','etat','create_at','update_at')

class commande_detailadmin(admin.ModelAdmin):
    list_display = ('commande','lemenu','prixunitaire','pu_promo','quantite','prixtotal','prixtotal_ligne_promo','create_at','update_at')


class niveaumatchadmin(admin.ModelAdmin):
    list_display = ('niveau_match','date_debut','date_fin')



class listematchchadmin(admin.ModelAdmin):
    list_display = ('libelle','niveau_match','equipe1','equipe2','estencours','dateheure')

class lematchadmin(admin.ModelAdmin):
    list_display = ('listematch','commande','Stade','entree','porte','zone','escalier','bloc','rang','siege')

class Locationadmin(admin.ModelAdmin):
    list_display = ('inscription','latitude','longitude','ref')

class menu_stadeadmin(admin.ModelAdmin):
    list_display = ('stade','libelle','estactif','image')

class menu_restaurantadmin(admin.ModelAdmin):
    list_display = ('libelle','estactif','image')

class Gallerieadmin(admin.ModelAdmin):
    list_display = ('libelle','estactif','estvideo','image','video')

admin.site.register(Gallerie,Gallerieadmin)
admin.site.register(menu_restaurant,menu_restaurantadmin)
admin.site.register(menu_stade,menu_stadeadmin)
admin.site.register(Location,Locationadmin)
admin.site.register(commende_match,lematchadmin)
admin.site.register(listematch,listematchchadmin)
admin.site.register(niveaumatch,niveaumatchadmin)
admin.site.register(commande_detail,commande_detailadmin)
admin.site.register(commande,commandeadmin)
admin.site.register(stade,stadeAdmin)
admin.site.register(inscription,clientadmin)
admin.site.register(codepromo,codepromoadmin)
admin.site.register(lemenu,menuadmin)
admin.site.register(typemenu,typemenuadmin)
