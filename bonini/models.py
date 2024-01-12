from django.db import models
import hashlib
from django_countries.fields import CountryField
from django.db.models.signals import pre_save
from django.dispatch import receiver
import phonenumbers
from location_field.models.plain import PlainLocationField
from mptt.models import MPTTModel, TreeForeignKey
# Create your models here.

class typemenu(models.Model):
    libelle = models.CharField(max_length=255)
    image = models.ImageField(upload_to='images/')
    def __str__(self) -> str:
        return self.libelle
    
class lemenu(models.Model):
    typemenu = models.ForeignKey(typemenu, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=255)
    prix = models.IntegerField()
    reduction = models.IntegerField()
    prixpromo = models.IntegerField()
    estactif = models.BooleanField(default=1)
    image = models.ImageField(upload_to='images/')
    def __str__(self) -> str:
        return self.libelle

class inscription(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.CharField(max_length=50,null=True)
    contact = models.CharField(max_length=50,null=True)
    pays = CountryField()
    ville = models.CharField(max_length=255,null=True)
    estclient = models.BooleanField(default=False)
    estinscriptparQR = models.BooleanField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    position_geographique = PlainLocationField(based_fields=['ville'], zoom=7,blank=True,null=True)  # Ajoutez ce champ
    def generate_promo_code(self):
        # Combinez les détails pertinents pour créer un code unique
        code_str = f"{self.nom}{self.prenom}{self.email}{self.contact}"
        
        # Utilisez une fonction de hachage pour créer un code de longueur fixe
        promo_code = hashlib.md5(code_str.encode()).hexdigest()
        
        # Vous voudrez peut-être tronquer le code ou ajouter un préfixe/suffixe selon vos besoins
        return promo_code[:10]  # Ajustez la longueur selon vos besoins
    
    def __str__(self) -> str:
        return self.nom
    
    def save(self, *args, **kwargs):
        # Assuming contact is a phone number without the country code
        if self.contact:
            # Assuming contact is a phone number without the country code
            phone_number = phonenumbers.parse(self.contact, self.pays.code)
            formatted_phone = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
            self.contact = formatted_phone
        super().save(*args, **kwargs)
    
class codepromo(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    estvalide = models.BooleanField()
    estutilise = models.BooleanField()
    dureevalidite = models.IntegerField()
    dateexpiration = models.DateField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.code

class menuvisite(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    lemenu = models.ForeignKey(lemenu, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class commande(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    codepromo = models.ForeignKey(codepromo, on_delete=models.CASCADE,null=True)
    ref = models.CharField(max_length=15,null=True) 
    quantite = models.IntegerField()
    prixtotal = models.IntegerField()
    nbarticle = models.IntegerField(null=True)
    estfacture = models.BooleanField(default=False)
    etat = models.CharField(max_length=50) # en cours de preparation, en cours de facturation, facturée, en cours de livraison, commande livrée, commande annulée
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def save(self, *args, **kwargs):
        # Update estclient attribute in the related inscription instance
        self.inscription.estclient = True
        self.inscription.save()

        # Call the original save method to save the commande instance
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.ref
    
class commande_detail(models.Model):
    commande = models.ForeignKey(commande, on_delete=models.CASCADE)
    lemenu = models.ForeignKey(lemenu, on_delete=models.CASCADE)
    prixunitaire = models.IntegerField()
    pu_promo = models.IntegerField()
    quantite = models.IntegerField()
    prixtotal = models.IntegerField()
    prixtotal_ligne_promo = models.IntegerField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def __str__(self) -> str:
        return self.lemenu.libelle


class facture(models.Model):
    commande = models.ForeignKey(commande, on_delete=models.CASCADE)
    pu_normal = models.IntegerField()
    pu_promo = models.IntegerField()
    quantite = models.IntegerField()
    prixtotal_ligne_normal = models.IntegerField()
    prixtotal_ligne_promo = models.IntegerField()
    tva = models.IntegerField()
    prixtotal_normal = models.IntegerField()
    prixtotal_promo = models.IntegerField()
    etat = models.CharField(max_length=50) # en attente de paiement, payé, annulée 
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class stade(MPTTModel):
    name = models.CharField(max_length=50)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return self.name
    
class niveaumatch(models.Model):
    niveau_match = models.CharField(max_length=255) # Phase éliminatoire, 8ème de finale, quart de fin, demie finale, match de classement, finale
    date_debut = models.DateField(null=True)
    date_fin = models.DateField(null=True)
    def __str__(self) -> str:
        return self.niveau_match

class listematch(models.Model):
    niveau_match = models.ForeignKey(niveaumatch, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=255)
    equipe1 = CountryField()
    equipe2 = CountryField()
    estencours = models.BooleanField(default=False)
    dateheure = models.DateTimeField()
    def __str__(self) -> str:
        return self.libelle
    
class commende_match(models.Model):
    listematch = models.ForeignKey(listematch, on_delete=models.CASCADE)
    commande = models.ForeignKey(commande, on_delete=models.CASCADE)
    Stade = models.CharField(max_length=255)
    entree = models.CharField(max_length=50)
    porte = models.CharField(max_length=50)
    zone = models.CharField(max_length=50)
    escalier = models.CharField(max_length=50)
    bloc = models.CharField(max_length=50)
    rang = models.CharField(max_length=50)
    siege = models.CharField(max_length=50)
    trouve_sur_place = models.BooleanField(default=False)


# from django.contrib.gis.db import models

# class PointOfInterest(models.Model):
#     name = models.CharField(max_length=255)
#     location = models.PointField()