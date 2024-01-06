from django.db import models
import hashlib

# Create your models here.

class typemenu(models.Model):
    libelle = models.CharField(max_length=255)
    image = models.CharField(max_length=255)

class lemenu(models.Model):
    typemenu = models.ForeignKey(typemenu, on_delete=models.CASCADE)
    libelle = models.CharField(max_length=255)
    prix = models.IntegerField()
    reduction = models.IntegerField()
    prixpromo = models.IntegerField()
    estactif = models.BooleanField(default=1)
    image = models.CharField(max_length=255)


class inscription(models.Model):
    nom = models.CharField(max_length=255)
    prenom = models.CharField(max_length=255)
    email = models.CharField(max_length=50,null=True)
    contact = models.CharField(max_length=50,null=True)
    pays = models.CharField(max_length=255)
    ville = models.CharField(max_length=255,null=True)
    estclient = models.BooleanField()
    estinscriptparQR = models.BooleanField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    def generate_promo_code(self):
        # Combinez les détails pertinents pour créer un code unique
        code_str = f"{self.nom}{self.prenom}{self.email}{self.contact}"
        
        # Utilisez une fonction de hachage pour créer un code de longueur fixe
        promo_code = hashlib.md5(code_str.encode()).hexdigest()
        
        # Vous voudrez peut-être tronquer le code ou ajouter un préfixe/suffixe selon vos besoins
        return promo_code[:10]  # Ajustez la longueur selon vos besoins
    
    def __str__(self) -> str:
        return self.nom
    
class codepromo(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    code = models.CharField(max_length=50)
    estvalide = models.BooleanField()
    estutilise = models.BooleanField()
    dureevalidite = models.IntegerField()
    dateexpiration = models.DateField()
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class menuvisite(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    lemenu = models.ForeignKey(lemenu, on_delete=models.CASCADE)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

class commande(models.Model):
    inscription = models.ForeignKey(inscription, on_delete=models.CASCADE)
    lemenu = models.ForeignKey(lemenu, on_delete=models.CASCADE)
    codepromo = models.ForeignKey(codepromo, on_delete=models.CASCADE,null=True)
    prixunitaire = models.IntegerField()
    quantite = models.IntegerField()
    prixtotal = models.IntegerField()
    etat = models.CharField(max_length=50) # en cours de preparation, en cours de facturation, en cours de livraison, commande satisfaite, commande annulée
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

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


