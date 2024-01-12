from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import inscription,lemenu,codepromo,stade,commande,commande_detail,commende_match,listematch
from .forms import InscriptionForm
from django.http import HttpResponse, JsonResponse
# Create your views here.
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django_countries import countries
from django.views.decorators.csrf import csrf_exempt
import hashlib
from decimal import Decimal  # Import Decimal for accurate decimal arithmetic
from django.template import loader


def generate_reference(quantite,prixtotal,create_at):
        # Combinez les détails pertinents pour créer un code unique
    code_str = f"{quantite}{prixtotal}{create_at}"
        
        # Utilisez une fonction de hachage pour créer un code de longueur fixe
    promo_code = hashlib.md5(code_str.encode()).hexdigest()
        
        # Vous voudrez peut-être tronquer le code ou ajouter un préfixe/suffixe selon vos besoins
    return promo_code[:10]  # Ajustez la longueur selon vos besoins

@csrf_exempt
def menu(request, inscription_id):
    # Récupérez l'instance à l'aide de l'ID
    request.session['inscription_id'] = inscription_id
    
    inscription_instance = get_object_or_404(inscription, pk=inscription_id)
    menus = lemenu.objects.filter(estactif=1)
    promo_code = inscription_instance.generate_promo_code()

    cart_data = request.session.get('cart_data_obj',{})
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

    request.session['promo_code_id'] = codepromo_instance.id
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

@csrf_exempt
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

@csrf_exempt

def addToCart(request):
    cart_restaurant = {}

    cart_restaurant[str(request.GET['id'])] = {
      'nomArticle': request.GET['nomArticle'],
      'prix': int(request.GET['prix']),

    'imageUrl': str(request.GET['imageUrl']),
      'quantite': 1,
      'total': 0,
    }
    
    diminuer = request.GET['diminuer']

    if 'cart_data_obj' in request.session:
      if str(request.GET['id']) in request.session['cart_data_obj']:
        cart_data = request.session['cart_data_obj']
        if diminuer == "true":
            if cart_data[str(request.GET['id'])]['quantite'] > 1:
                cart_data[str(request.GET['id'])]['quantite'] -= 1
        else:
            cart_data[str(request.GET['id'])]['quantite'] += 1
        
        prix = int(cart_data[str(request.GET['id'])]['prix'])
        qte = int(cart_data[str(request.GET['id'])]['quantite'])
        
        total = prix * qte
        cart_data[str(request.GET['id'])]['total'] = total
        
        cart_data.update(cart_data)
        request.session['cart_data_obj'] = cart_data
      else:
        cart_data = request.session['cart_data_obj']
        cart_data.update(cart_restaurant)
        request.session['cart_data_obj'] = cart_data
    else:
         # C'est un nouvel enregistrement, calculer le montant total
        cart_data = cart_restaurant
        prix_nouveau = int(cart_data[str(request.GET['id'])]['prix'])
        qte_nouveau = int(cart_data[str(request.GET['id'])]['quantite'])

        total_nouveau = prix_nouveau * qte_nouveau
        cart_restaurant[str(request.GET['id'])]['total'] = total_nouveau

        request.session['cart_data_obj'] = cart_restaurant
    
     # Calcul du montant total général pour tous les articles dans le panier
    total_general = sum(item.get('total', 0) for item in cart_data.values())
    return JsonResponse({"data": request.session['cart_data_obj'], 'totaldocuments': len(request.session['cart_data_obj']), 'total_general': total_general})

@csrf_exempt
def removeFromCart(request):
    if 'cart_data_obj' in request.session:
        document_id = request.GET.get('id')
        if document_id in request.session['cart_data_obj']:
            del request.session['cart_data_obj'][document_id]
            request.session.modified = True

            cart_data = request.session['cart_data_obj']
            
            total_general = sum(item.get('total', 0) for item in cart_data.values())

            context = {
                'panier': cart_data,
                'total_general': total_general,
            }

    template = loader.get_template('panier_item.html')

    return HttpResponse(template.render(context, request=request))

def updateCart(request):
    diminuer = request.GET['diminuer']
    
    if 'cart_data_obj' in request.session:
      if str(request.GET['id']) in request.session['cart_data_obj']:
        cart_data = request.session['cart_data_obj']
        if diminuer == "true":
            if cart_data[str(request.GET['id'])]['quantite'] > 1:
                cart_data[str(request.GET['id'])]['quantite'] -= 1
        else:
            cart_data[str(request.GET['id'])]['quantite'] += 1
        
        prix = int(cart_data[str(request.GET['id'])]['prix'])
        qte = int(cart_data[str(request.GET['id'])]['quantite'])
        
        total = prix * qte
        cart_data[str(request.GET['id'])]['total'] = total
        
        cart_data.update(cart_data)
        request.session['cart_data_obj'] = cart_data
        
        # Calcul du montant total général pour tous les articles dans le panier
        total_general = sum(item.get('total', 0) for item in cart_data.values())

        context = {
            'panier': cart_data,
            'total_general': total_general,
        }

        template = loader.get_template('panier_item.html')

        return HttpResponse(template.render(context, request=request))
      
@csrf_exempt
def ouvrirpanier(request):
    cart_data = request.session.get('cart_data_obj',{})
    total_general = sum(item.get('total', 0) for item in cart_data.values())
    
    stades = stade.objects._mptt_filter(level=0)
    
    context = {
        'stades':stades,
        'panier': cart_data,
        'total_general': total_general,
    }
    return render(request,'checkout.html',context)

@csrf_exempt
def recupererDonnesStades(request):
    id = request.POST.get('id')
    
    stades_data = stade.objects._mptt_filter(parent_id=id).values()
    
    # stades_list = [model_to_dict(stade_obj) for stade_obj in stades_data]
    stades_list = list(stades_data)
    
    # return JsonResponse({"data": stades_list})
    return JsonResponse({"data":stades_list})

def commander(request):
    if request.method == 'POST':
        Stade = request.POST.get('Stade')
        entree = request.POST.get('Entree')
        porte = request.POST.get('Porte')
        zone = request.POST.get('zone')
        escalier = request.POST.get('escalier')
        bloc = request.POST.get('bloc')
        rang = request.POST.get('rang')
        Siege = request.POST.get('Siege')
        austade = request.POST.get('checkout[position][id]')

        panier = request.session.get('cart_data_obj',{})
        total_general = sum(item.get('total', 0) for item in panier.values())
        qte_total = sum(item.get('quantite', 0) for item in panier.values())
        create_at = datetime.now()

        inscription_id = request.session.get('inscription_id', None)
        promo_code_id = request.session.get('promo_code_id', None)
        

        inscription_instance = get_object_or_404(inscription, pk=inscription_id)
        codepromo_instance = get_object_or_404(codepromo, pk=promo_code_id)
        commande_instance = commande.objects.create(
                inscription=inscription_instance,
                codepromo=codepromo_instance,
                ref=generate_reference(qte_total,total_general,create_at),
                quantite=qte_total,
                prixtotal=total_general,
                etat='en cours de preparation',
            )
        commande_id = commande_instance.id
        
        commande_instance = get_object_or_404(commande, pk=commande_id)
        if austade ==1:
            liste_match = listematch.objects.get(estencours=1)
            listematch_instance = get_object_or_404(listematch, pk=liste_match.id)
    
            commende_match_instance = commende_match.objects.create(
                commande=commande_instance,
                listematch=listematch_instance,
                Stade=Stade,
                entree=entree,
                porte=porte,
                zone=zone,
                escalier=escalier,
                bloc=bloc,
                rang=rang,
                siege=Siege,
            )
        
        nbarticle = 0
        for article_id, article_data in panier.items():
            nom_article = article_data['nomArticle']
            prix = article_data['prix']
            image_url = article_data['imageUrl']
            quantite = article_data['quantite']
            total = article_data['total']
            nbarticle +=1

            lemenu_instance = get_object_or_404(lemenu, pk=article_id)
            
            prixtotal_ligne_promo = Decimal(lemenu_instance.prixpromo) * Decimal(quantite)

            commande_detail_instance = commande_detail.objects.create(
                commande=commande_instance,
                lemenu=lemenu_instance,
                prixunitaire=prix,
                quantite=quantite,
                prixtotal=total,
                pu_promo=lemenu_instance.prixpromo,
                prixtotal_ligne_promo=prixtotal_ligne_promo,
            )
        commande_instance.nbarticle = nbarticle
        commande_instance.save()
    # vider le panier
    request.session.pop('cart_data_obj', None)
    # créer une nouvelle instance de "cart_data_obj" vide
    request.session['cart_data_obj']={}

    return JsonResponse({"data":panier})