from django.db import models
from django.contrib.auth.models import User
from django.forms import ModelForm
from phonenumber_field.modelfields import PhoneNumberField
from django.urls import reverse
from rest_framework.reverse import reverse as api_reverse
from django.conf import settings

# Create your models here.

class Abonne(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telephone = PhoneNumberField()
    def __str__(self):
        return '%s' % self.user

class Fournisseur(models.Model):
    nom=models.CharField(unique=True, max_length=70)
    adresse=models.CharField(max_length=70)
    produits_fournis=models.CharField(max_length=50)
    telephone=PhoneNumberField()
    status=models.CharField(max_length=20, default='Valide')
    def __str__(self):
        return '%s' % self.nom

class Employe(models.Model):
    OPTIONS=[]
    OPTIONS.append(("Administrateur du projet", "P1"))
    OPTIONS.append(("Livreur", "P2"))
    OPTIONS.append(("Informaticien", "P3"))
    user=models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    telephone=PhoneNumberField()
    poste=models.CharField(max_length=70, choices=OPTIONS)
    def __str__(self):
        return '%s' % self.user 

class Categorie(models.Model):
    nom=models.CharField(unique=True ,max_length=80)
    image=models.ImageField()
    image2=models.ImageField()
    def __str__(self):
        return '%s' % self.nom

class SousCategorie(models.Model):
    nom=models.CharField(unique=True, max_length=80)
    categorie=models.ForeignKey(Categorie, related_name='souscategories',  on_delete=models.CASCADE)
    def __str__(self):
        return '%s' % self.nom

    def get_api_url(self, request):
        return api_reverse("articles-sc", kwargs={'id':self.pk}, request=request)
        
    def get_category_name(self):
        return self.categorie.nom

class Article(models.Model):
    nom = models.CharField(unique=True ,max_length=50, blank=True)
    description= models.TextField(blank=True)
    quantite = models.IntegerField(default=0)
    image_present= models.ImageField()
    sous_categorie=models.ForeignKey(SousCategorie, related_name='articles', on_delete=models.CASCADE)
    prix_present=models.IntegerField()
    prev_prix_present=models.IntegerField(blank=True, null=True)
    fournisseur=models.ForeignKey(Fournisseur, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return '%s' % self.nom

    def get_api_url(self, request):
        return api_reverse("article", kwargs={'id':self.pk}, request=request)

class SousArticle(models.Model):
    article=models.ForeignKey(Article, related_name='sousarticles' ,on_delete=models.CASCADE)
    prev_prix=models.IntegerField(blank=True, null=True)
    prix = models.IntegerField()
    quantite = models.IntegerField()
    def __str__(self):
        return  str(self.article) +'  '+str(self.id)

class Photo(models.Model):
    photo=models.ImageField()
    article=models.ForeignKey(Article, on_delete=models.CASCADE)
    def __str__(self):
        return '%s' % self.article

class Panier(models.Model):
    STATUTS = []
    STATUTS.append(('finalisé', 'finalisé'))
    STATUTS.append(('non finalisé', 'non finalisé'))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    total = models.IntegerField(default=0)
    statut = models.CharField(max_length=40, choices=STATUTS, default='non finalisé')
    def get_api_url(self, request):
        return api_reverse("panier", kwargs={'id':self.pk}, request=request)


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, related_name='lignespanier', on_delete=models.CASCADE)
    s_article = models.ForeignKey(SousArticle, on_delete=models.CASCADE)
    prixunitaire = models.IntegerField()
    quantite = models.IntegerField(default=1)

class Caracteristique(models.Model):
    caracteristique=models.CharField(max_length=80)
    s_article=models.ForeignKey(SousArticle, related_name='caracteristiques' , on_delete=models.CASCADE)
    valeur=models.CharField(max_length=70)
    def __str__(self):
        return '%s' % self.s_article


class CommandeClient(models.Model):
    StatesCom=[]
    StatesCom.append(("Livrée", "Livrée"))
    StatesCom.append(("En attente de livraison", "Wait"))
    StatesCom.append(("Annulée", "Annulée"))
    ModeBuy=[]
    ModeBuy.append(("A la livraison", "ALaLiv"))
    ModeBuy.append(("MTN MoMo", "MTN"))
    ModeBuy.append(("Orange MoMo", "OR"))
    ModeLiv=[]
    ModeLiv.append(('Standard', 'St'))
    ModeLiv.append(('Express', 'Ex'))
    ModeLiv.append(('Recupération par le client', 'ReClient'))
    abonne=models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date=models.DateTimeField(auto_now_add=True)
    date_livraison=models.DateTimeField(null=True, blank=True)
    frais_livraison=models.IntegerField(default=0)
    totalpaye=models.IntegerField(default=0)
    lieu_livraison=models.CharField(default=" ", max_length=500, blank=True)
    mode_paiement=models.CharField(max_length=60, choices=ModeBuy, default="A la livraison")
    etat=models.CharField(max_length=50, choices=StatesCom, default="En attente de livraison")
    mode_livraison=models.CharField(max_length=50, choices=ModeLiv, default="Standard")
    livreur=models.ForeignKey(Employe, null=True, blank=True, on_delete=models.SET_NULL)
    panier=models.OneToOneField(Panier, on_delete=models.CASCADE)

class Promotion(models.Model): 
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    reduction=models.FloatField(default=0)
    debut_promotion=models.DateTimeField()
    fin_promotion=models.DateTimeField()

class VilleLivraison(models.Model):
    nom=models.CharField(max_length=60)
    def __str__(self):
        return '%s' % self.nom
    
class PointLivraison(models.Model):
    nom=models.CharField(max_length=50)
    ville=models.ForeignKey(VilleLivraison, on_delete=models.CASCADE)
    def __str__(self):
        return '%s' % self.nom
    
class CategToHome(models.Model):
    nom=models.CharField(unique=True, max_length=60)
    def __str__(self):
        return '%s' % self.nom

class ArticleToHome(models.Model):
    article=models.OneToOneField(Article, related_name='article', on_delete=models.CASCADE)
    categorieToHome=models.ForeignKey(CategToHome, related_name='articlestohome', on_delete=models.CASCADE)
    def __str__(self):
        return '%s' % self.article