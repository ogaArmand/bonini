from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import inscription,lemenu,codepromo
from .forms import InscriptionForm
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django_countries import countries

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

    cart_data = request.session.get('cart_data_obj', {})
    # Utilisez l'instance dans votre modèle
    context = {
        'inscription_instance': inscription_instance,
        'codepromo_instance': codepromo_instance,
        'menus':menus,
        'promo_code':promo_code,
        'panier': cart_data,
     }
    return render(request, 'menu.html',context)


def index(request):
    return render(request,'type-1.html')

def formulaire(request,qr):
    form = InscriptionForm()
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
        'qr':qr,
        'form': form,
    }
    return render(request, 'reservation.html',context)



def obtenir_liste_pays():
    return [(code, nom) for code, nom in list(countries)]


def addToCart(request):
    cart_restaurant = {}

    cart_restaurant[str(request.GET['id'])] = {
      'nomArticle': request.GET['nomArticle'],
      'prix': str(request.GET['prix']),
      'imageUrl': str(request.GET['imageUrl']),
    }

    if 'cart_data_obj' in request.session:
      if str(request.GET['id']) in request.session['cart_data_obj']:
         pass
         cart_data = request.session['cart_data_obj']
         cart_data[str(request.GET['id'])]['nomArticle'] = cart_restaurant[str(request.GET['id'])]['nomArticle']
         cart_data[str(request.GET['id'])]['prix'] = cart_restaurant[str(request.GET['id'])]['prix']
         cart_data[str(request.GET['id'])]['imageUrl'] = cart_restaurant[str(request.GET['id'])]['imageUrl']
         cart_data.update(cart_data)
         request.session['cart_data_obj'] = cart_data
      else:
        cart_data = request.session['cart_data_obj']
        cart_data.update(cart_restaurant)
        request.session['cart_data_obj'] = cart_data
    else:
      request.session['cart_data_obj'] = cart_restaurant
    
    return JsonResponse({"data": request.session['cart_data_obj'], 'totaldocuments': len(request.session['cart_data_obj'])})

def removeFromCart(request):
    if 'cart_data_obj' in request.session:
        document_id = request.GET.get('id')
        if document_id in request.session['cart_data_obj']:
            del request.session['cart_data_obj'][document_id]
            request.session.modified = True

            return JsonResponse({"data":request.session['cart_data_obj'], 'totaldocuments': len(request.session['cart_data_obj'])})
    return JsonResponse({"message": "Document non trouvé dans le panier"})

def ouvrirpanier(request):
    pass