from django.shortcuts import render
from django.shortcuts import render, redirect
from .models import inscription,lemenu,codepromo,stade,menu_stade,menu_restaurant,commande,commande_detail,commende_match,listematch,Location,Gallerie
from .forms import InscriptionForm
from django.http import HttpResponse, JsonResponse, FileResponse
# Create your views here.
from django.shortcuts import render, get_object_or_404
from datetime import datetime, timedelta
from django_countries import countries
from django.views.decorators.csrf import csrf_exempt
import hashlib
from decimal import Decimal  # Import Decimal for accurate decimal arithmetic
from django.template import loader
import os
import requests
from django.views import View
import requests
import json


class MyCampaignView(View):
    def __init__(self, label, sender, contacts, content, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = label
        self.sender = sender
        self.contacts = contacts if isinstance(contacts, list) else [contacts]
        self.content = content
        print(label)
        print(sender)
        print(contacts)
        print(content)
   
        # Construire le payload
        payload = json.dumps({
            "label": self.label,
            "sender": self.sender,
            "contacts": self.contacts,
            "content": self.content
        })

        # Remplacer avec votre URL et token réels
        url = "https://apis.letexto.com/v1/campaigns"
        print(url)
        headers = {
            'Authorization': 'Bearer 34b7559f677cd31a16746a20ad1ae7',
            'Content-Type': 'application/json'
        }

        # Effectuer la requête POST
        response = requests.post(url, data=payload, headers=headers)
        print(response.status_code)
        print("Voici")
        # Vérifier si la requête a réussi (code de statut 2xx)
        if response.ok:
            print(response.status_code)
            print("OK III")
            data = response.json()
            return JsonResponse(data)
        else:
            # Gérer les erreurs
            error_data = {
                'error': f"Error: {response.status_code}",
                'details': response.text
            }
            print(error_data)
            print("OK")
            return JsonResponse(error_data, status=500)


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

def api_envoi_sms(numero,msg):
    url = "https://apis.letexto.com/v1/campaigns/sms"

    payload = json.dumps({
    "label": "Confirmation de l'inscription",
    "sender": "CAFE BONINI",
    "contacts": [
        {
        "age": "12",
        "numero": numero,
        "name": "Armand"
        },
    ],
    "content": msg
    })
    headers = {
    'Authorization': 'Bearer 8dfc810ed2da46aa2b4019b04dd52dfa',
    'Content-Type': 'application/json'
    }

    response = requests.post(url, data=payload, headers=headers)
    data = response.json()
    print(json.dumps(data))

@csrf_exempt
def formulaire(request,qr):
   
   if 'inscrit' in request.session:
       promo_code = request.session['inscrit']
       return redirect('menu_stade_restaurant',promo_code)
   else:
        
        form = InscriptionForm()
        stades = stade.objects._mptt_filter(level=0)
        if request.method == 'POST':
            # The form has been submitted
            nom = request.POST.get('nom')
            prenom = request.POST.get('prenom')
            email = request.POST.get('email')
            contact = request.POST.get('contact')
            pays = request.POST.get('pays')
            ville = request.POST.get('ville')
            stade_id = request.POST.get('stades')
            
            # Obtenir la date d'aujourd'hui
            aujourdhui = datetime.now()
            date_expiration_str = '20240213' #aujourdhui + duree
    # # Ajouter une durée de 30 jours
        # duree = timedelta(days=30)
            date_expiration = datetime.strptime(date_expiration_str, '%Y%m%d')
    # Calculer la durée entre les deux dates
            duree = date_expiration - aujourdhui
            estinscriptparQR = 0
            if qr == 1:
                estinscriptparQR=1
            # Perform validation if needed
            try:
                # Tentez de créer une nouvelle instance de 'inscription'
                stade_instance = get_object_or_404(stade, pk=stade_id)
                inscription_instance, created = inscription.objects.get_or_create(
                    contact=contact,
                    defaults={
                        'stade': stade_instance,
                        'nom': nom,
                        'prenom': prenom,
                        'email': email,
                        'pays': pays,
                        'ville': ville,
                        'estinscriptparQR': estinscriptparQR,
                        'estclient': 0
                    }
                )

                if not created:
                    # L'instance existe déjà, vous pouvez prendre des mesures en conséquence
                    print("L'inscription avec ce contact existe déjà.")

                promo_code = inscription_instance.generate_promo_code()
                codepromo_instance = codepromo.objects.create(
                    inscription=inscription_instance,
                    code=promo_code.upper() ,
                    estvalide=1,
                    estutilise=0,
                    dureevalidite=duree.days,
                    dateexpiration=date_expiration,
                    )
                msg = "Salut "+ prenom +", Votre code promo est : "+ promo_code.upper() + ". Vous bénéficiez de -20% sur vos achats au CAFE BONINI. site : https://www.bonini.ci"
                # L'enregistrement a été fait avec succès
                # Envoi de sms
                api_envoi_sms(contact,msg)
                request.session['inscrit'] = promo_code.upper() 
                return redirect('menu_stade_restaurant',promo_code.upper())
            except Exception as e:
                # Une exception s'est produite (par exemple, des erreurs de validation)
                error_message = str(e)
                return render(request, '404.html', {'error_message': error_message})
            
        context = {
        'qr':qr,
        'form': form,
        'stades':stades,
        }
        return render(request, 'reservation.html',context)



def obtenir_liste_pays():
    return [(code, nom) for code, nom in list(countries)]

@csrf_exempt
def addToCart(request):
    cart_restaurant = {}

    # cart_restaurant[str(request.GET['id'])] = {
    #   'nomArticle': request.GET['nomArticle'],
    #   'prix': int(request.GET['prix']),

    # 'imageUrl': str(request.GET['imageUrl']),
    #   'quantite': 1,
    #   'total': 0,
    # }
    cart_restaurant[str(request.GET['id'])] = {
      'nomArticle': request.GET['nomArticle'],
      'prix': int(request.GET['prix']),
      'imageUrl': str(request.GET['imageUrl']),
      'quantite': 1,
      'total': int(request.GET['prix']),
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
    
    id = request.GET.get('id')
    
    try:
        menustade = menu_stade.objects.get(id=id)
        
        # Vous pouvez adapter ce dictionnaire en fonction des champs de votre modèle
        menustade_data = {
            'id': menustade.id,
            'libelle': menustade.libelle,
            'estactif': menustade.estactif,
            'image': menustade.image,
            # Ajoutez d'autres champs ici
        }

        return JsonResponse({"data": menustade_data})
    except menu_stade.DoesNotExist:
        return JsonResponse({"error": "Stade non trouvé"}, status=404)

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
        
        ref=generate_reference(qte_total,total_general,create_at)

        inscription_instance = get_object_or_404(inscription, pk=inscription_id)
        codepromo_instance = get_object_or_404(codepromo, pk=promo_code_id)
        commande_instance = commande.objects.create(
                inscription=inscription_instance,
                codepromo=codepromo_instance,
                ref=ref,
                quantite=qte_total,
                prixtotal=total_general,
                etat='en cours de preparation',
            )
        commande_id = commande_instance.id

        # mettre à jour la localisation
        Location_id = request.session.get('Location_id', None)
        Location_instance = get_object_or_404(Location, pk=Location_id)
        Location_instance.ref = ref
        Location_instance.save()

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
    context = {
        'inscription_id':inscription_id
    }
    return render(request,'ordered.html',context)



def telecharger_menu(request):
    chemin_pdf = 'bonini/static/assets/images/menu.pdf'

    if os.path.exists(chemin_pdf):
        with open(chemin_pdf, 'rb') as pdf_file:
            response = HttpResponse(pdf_file.read(), content_type='application/pdf')
            response['Content-Disposition'] = 'inline; filename="votre_fichier.pdf"'
            return response
    else:
        return render(request, '404.html')

def enregistrer_coordonnees(request):
    if request.method == 'POST':
        ref = request.POST.get('ref')
        inscription_id = request.session.get('inscription_id', None)
        inscription_instance = get_object_or_404(inscription, pk=inscription_id)
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        new_location = Location(inscription=inscription_instance,latitude=latitude, longitude=longitude)
        new_location.save()
        request.session['Location_id'] = new_location.id

        return JsonResponse({'message': 'Coordonnées enregistrées avec succès.'})
    else:
        return JsonResponse({'message': 'Méthode non autorisée.'},status=405)
    
def suivi_commande(request):
    commandes = commande.objects.all()
    context = {
        'commandes':commandes
    }
    return render(request,'suividescommandes.html',context)



def localiser_sur_google_maps(request,ref):
    # Récupérer les coordonnées de latitude et de longitude depuis votre modèle
    objet = Location.objects.get(ref=ref)  # Remplacez par l'objet que vous souhaitez localiser
    lat = objet.latitude
    lon = objet.longitude

    # Construire le lien Google Maps avec les paramètres de latitude et de longitude
    google_maps_link = f'https://www.google.com/maps/place/{lat},{lon}'
    # https://www.google.com/maps/@{lat},-4.0206286,18.38z?entry=ttu

    # Rediriger l'utilisateur vers le lien Google Maps
    return redirect(google_maps_link)

def menu_stade_restaurant(request,promo_code):
    stades = stade.objects._mptt_filter(level=0)
    menu_restaurants = menu_restaurant.objects.get(estactif=1)
    gallerie_img = Gallerie.objects.filter(estactif=1,estvideo=0)
    gallerie_vid = Gallerie.objects.filter(estactif=1,estvideo=1)
    context ={
        'stades':stades,
        'menu_restaurants':menu_restaurants,
        'gallerie_img':gallerie_img,
        'gallerie_vid':gallerie_vid,
        'promo_code':promo_code
    }
    return render(request,'choixmenu.html',context)

@csrf_exempt
def get_menu_image(request):
    try:
        id = int(request.GET.get('id'))
    except (ValueError, TypeError):
        # Handle the case where 'id' is not a valid integer
        data = {'error': 'Invalid or missing id parameter.'}
        return JsonResponse(data)
    
    stades = get_object_or_404(stade, pk=id)
    menu = menu_stade.objects.get(stade=stades)
    
    if not menu:
        data = {'error': 'Menu not found for the provided id.'}
        return JsonResponse(data)

    data = {
        'menu': {
            'id': menu.id,
            'image_url': menu.image.url,
            # Add other relevant fields from your 'menu_stade' model
        }
    }

    return JsonResponse(data)

def gallerie(request):
    gallerie_img = Gallerie.objects.filter(estactif=1,estvideo=0)
    gallerie_vid = Gallerie.objects.filter(estactif=1,estvideo=1)

    context = {
        'gallerie_img':gallerie_img,
        'gallerie_vid':gallerie_vid,
    }
    return render(request,'',context)



# api_envoi_sms('2250544169597','Test bonini.ci')