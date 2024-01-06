from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import inscription,lemenu,codepromo
from django.http import HttpResponse
# Create your views here.
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta

def menu(request, inscription_id):
    # Récupérez l'instance à l'aide de l'ID
    inscription_instance = get_object_or_404(inscription, pk=inscription_id)
    menus = lemenu.objects.filter(estactif=1)
    promo_code = inscription_instance.generate_promo_code()
    
# Obtenir la date d'aujourd'hui
    aujourdhui = datetime.now()
    date_expiration_str = '20240213' #aujourdhui + duree
# # Ajouter une durée de 30 jours
    # duree = timedelta(days=30)
    date_expiration = datetime.strptime(date_expiration_str, '%Y%m%d')
# Calculer la durée entre les deux dates
    duree = date_expiration - aujourdhui

    codepromo_instance = codepromo.objects.create(
                inscription=inscription_instance,
                code=promo_code,
                estvalide=1,
                estutilise=0,
                dureevalidite=duree.days,
                dateexpiration=date_expiration,
    )


    # Utilisez l'instance dans votre modèle
    context = {
        'inscription_instance': inscription_instance,
        'codepromo_instance': codepromo_instance,
        'menus':menus,
        'promo_code':promo_code
     }
    return render(request, 'menu.html',context)


def index(request):
    return render(request,'menu.html')

def formulaire(request,qr):

    if request.method == 'POST':
        # The form has been submitted
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        contact = request.POST.get('contact')
        pays = request.POST.get('pays')
        ville = request.POST.get('ville')

        estinscriptparQR = 0
        if qr == 1:
            estinscriptparQR=1
        # Perform validation if needed
        try:
            # Tentez de créer une nouvelle instance de 'inscription'
            inscription_instance = inscription.objects.create(
                nom=nom,
                prenom=prenom,
                email=email,
                contact=contact,
                pays=pays,
                ville=ville,
                estinscriptparQR=estinscriptparQR,
                estclient=0
            )
            
            # L'enregistrement a été fait avec succès
            return redirect('menu', inscription_id=inscription_instance.id)
        except Exception as e:
            # Une exception s'est produite (par exemple, des erreurs de validation)
            error_message = str(e)
            return render(request, '404.html', {'error_message': error_message})
    
    context = {
        'qr':qr
    }
    return render(request, 'reservation.html',context)