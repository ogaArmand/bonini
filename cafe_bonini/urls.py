"""cafe_bonini URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from bonini.views import menu,formulaire,index,addToCart,ouvrirpanier,removeFromCart,recupererDonnesStades,commander,updateCart,telecharger_menu
from bonini.views import enregistrer_coordonnees,suivi_commande,localiser_sur_google_maps,MyCampaignView
from bonini.views import telecharger_menu,menu_stade_restaurant,get_menu_image
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('<int:qr>/', formulaire, name='formulaire'),
    # path('', formulaire, {'qr': 1}, name='formulaire'),
    path('menu/<int:inscription_id>/', menu, name='menu'),
    # path('TB1', TB1, name='TB1'),ref
    path('', index, name='index'),
    path('addToCart', addToCart, name='addToCart'),
    path('ouvrirpanier', ouvrirpanier, name='ouvrirpanier'),
    path('removeFromCart', removeFromCart, name='removeFromCart'),
    path('recupererDonnesStades', recupererDonnesStades, name='recupererDonnesStades'),
    path('get_menu_image', get_menu_image, name='get_menu_image'),
    path('commander', commander, name='commander'),
    path('updateCart', updateCart, name='updateCart'),
    path('telecharger_menu', telecharger_menu, name='telecharger_menu'),
    path('enregistrer_coordonnees', enregistrer_coordonnees, name='enregistrer_coordonnees'),
    path('suivi_commande', suivi_commande, name='suivi_commande'),
    path('menu_stade_restaurant/<str:promo_code>', menu_stade_restaurant, name='menu_stade_restaurant'),
    path('localiser_sur_google_maps/<str:ref>/', localiser_sur_google_maps, name='localiser_sur_google_maps'),
    # path('my-campaign/', MyCampaignView.as_view(), name='my_campaign_view'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)