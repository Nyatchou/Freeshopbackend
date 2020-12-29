from freeshop.models import *
from freeshop.api.serializers import *
from rest_framework import generics, mixins , response, status, views
from django.shortcuts import redirect
from rest_framework.reverse import reverse 
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from datetime import datetime
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialLoginView
from rest_framework.authtoken.models import Token
from rest_framework.pagination import PageNumberPagination
from rest_framework import filters

class HomeView(generics.ListAPIView):
    serializer_class = CategToHomeSerializer

    def get_queryset(self):
        return CategToHome.objects.all()
        
    def get(self, request , *args , **kwargs):
        for item in self.get_queryset():
            for articlehome in ArticleToHome.objects.filter(categorieToHome=item):
                promot_manager = PromotManager()
                promot_manager.applyorstop_promotion(articlehome.article)
        categsToHome = self.serializer_class(self.get_queryset(), many=True).data
        for categ in categsToHome:
            for articlehome in categ['articlestohome']:
                if articlehome['article']['quantite'] <= 0:
                    categsToHome['articlestohome'].remove(articlehome)
                articlehome['article'].pop('quantite')

        return response.Response(data=categsToHome, status=status.HTTP_200_OK)


class CategorieListAPIView(generics.ListAPIView):
    serializer_class = CategorieSerializer
    pagination_class = None

    def get_queryset(self):
        return Categorie.objects.all()


class ArticlesSousCategorieView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = SousCategorieSerializer

    def get_queryset(self):
        return SousCategorie.objects.all()


    def get(self, request , *args , **kwargs):
        query = self.get_object()
        articles = Article.objects.filter(sous_categorie = query)
        for article in articles :
            promot_manager = PromotManager()
            promot_manager.applyorstop_promotion(article)
        sous_categorie = self.serializer_class(query , many=False).data  
        for article in sous_categorie['articles']:
            if article['quantite'] <= 0:
                sous_categorie['articles'].remove(article)
            article.pop('quantite')
        return response.Response(data=sous_categorie, status=status.HTTP_200_OK)

class ArticlesSousCategorieAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer

    def get_queryset(self):
        nom_categorie = self.kwargs.get('categorie')
        nom_souscategorie = self.kwargs.get('souscategorie')
        categorie = Categorie.objects.get(nom=nom_categorie)
        souscategorie = SousCategorie.objects.get(nom=nom_souscategorie, categorie=categorie)
        articles = Article.objects.filter(sous_categorie=souscategorie, quantite__gt=0)
        for article in articles :
            promot_manager = PromotManager()
            promot_manager.applyorstop_promotion(article)
        return articles

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

class ArticlesListAPIView(generics.ListAPIView):
    serializer_class = ArticleSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nom', 'sous_categorie__nom', 'sous_categorie__categorie__nom']
    ordering_fields = ['prix_present']

    def get_queryset(self):
        id_sc = self.kwargs.get('id_sc')
        souscategorie = SousCategorie.objects.get(pk=id_sc)
        articles0 = Article.objects.filter(sous_categorie=souscategorie, quantite__gt = 0)
        for article in articles0 :
            promot_manager = PromotManager()
            promot_manager.applyorstop_promotion(article)
        return articles0


    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class ArticleRetrieveAPIView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = ArticleExpandedSerializer
    queryset = Article.objects.all()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def get(self, request , *args , **kwargs):
        query = self.get_object()
        if query.quantite <= 0 :
            return response.Response(data={}, status=status.HTTP_200_OK)    
        promot_manager = PromotManager()
        promot_manager.applyorstop_promotion(query)    
        data = self.serializer_class(query, many=False).data
        for item in data['sousarticles']:
            item.pop('article')
            for itemc in item['caracteristiques']:
                itemc.pop('s_article')     
            
        return response.Response(data=data, status=status.HTTP_200_OK)

class LignesPanierListView(generics.ListCreateAPIView):
    serializer_class = LignePanierSerializer
    permission_class = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        panier = Panier.objects.get_or_create(user=user, statut='non finalisé')
        return LignePanier.objects.filter(panier=panier[0])

    def get(self, request , *args , **kwargs):
        query = self.get_queryset()
        data = self.serializer_class(query, many=True).data

        for item in data:
            sousarticle = SousArticle.objects.get(pk=item['s_article'])
            article = ArticleSerializer(sousarticle.article).data
            sous_article = {
                'id' : item.pop('s_article'),
                'image_url' : article['image_present'],
                'quantite_max' : sousarticle.quantite,
                'nom': article['nom'],
            }
            item['sousarticle'] = sous_article 
            item.pop('panier')    
        
        return response.Response(data=data, status=status.HTTP_200_OK) 

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

class PanierRUAPIView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = PanierSerializer
    queryset = Panier.objects.all()

    def get(self, request , *args , **kwargs):
        query = self.get_object()
        data = self.serializer_class(query, many=False).data

        for item in data['lignespanier']:

            sousarticle = SousArticle.objects.get(pk=item['s_article'])
            article = ArticleSerializer(sousarticle.article).data
            sous_article = {
                'id' : item.pop('s_article'),
                'image_url' : article['image_present'],
                'quantite_max' : sousarticle.quantite,
                'nom': article['nom'],
                'prix': sousarticle.prix
            }
            item['sousarticle'] = sous_article

            # item['sousarticle']['id'] = item.pop('s_article'),
            # item['sousarticle']['image_url'] = article.image_present
            # item['sousarticle']['quantite_max'] = sousarticle.quantite
            # item['sousarticle']['nom'] = article.nom
            # item['sousarticle']['prix'] = sousarticle.prix
            item.pop('panier')
        print(data)

        return response.Response(data=data, status=status.HTTP_200_OK) 

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

class PanierCreateAPIView(generics.CreateAPIView):
    serializer_class = PanierSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}


class LignePanierRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = 'id'
    serializer_class = LignePanierSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LignePanier.objects.all()

    def perform_destroy(self, instance):
        panier = instance.panier
        panier.total -= instance.prixunitaire * instance.quantite
        panier.save()
        instance.delete()

    def get_serializer_context(self, *args, **kwargs):
        return {"request": self.request}

    def get(self, request , *args , **kwargs):
        query = self.get_object()
        data = self.serializer_class(query, many=False).data
        sousarticle = SousArticle.objects.get(pk=data['s_article'])
        article = ArticleSerializer(sousarticle.article).data
        sous_article = {
            'id' : data.pop('s_article'),
            'image_url' : article['image_present'],
            'quantite_max' : sousarticle.quantite,
            'nom': article['nom'],
            'prix': sousarticle.prix
        }
        data['sousarticle'] = sous_article
        data.pop('panier')

        return response.Response(data=data, status=status.HTTP_200_OK)



class LignePanierCreateAPIView(generics.CreateAPIView):
    lookup_field = 'id'
    serializer_class = LignePanierSerializer
    permission_classes = [IsAuthenticated]
    

class CommandeClientCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommandeClientForClientSerializer
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        abonne = Abonne.objects.get(user = user)      
        return CommandeClient.objects.filter(abonne = abonne)   

    def perform_create(self, serializer):
        abonne,_ = Abonne.objects.get_or_create(user = self.request.user)
        serializer.save(abonne = abonne)

class CommandeClientRDAPIView(generics.RetrieveDestroyAPIView):
    lookup_field = 'id'
    serializer_class = CommandeClientForClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        abonne = Abonne.objects.get(user = user)      
        return CommandeClient.objects.filter(abonne = abonne)

    def perform_destroy(self, instance):
        panier = instance.panier
        for lipanier in LignePanier.objects.filter(panier=panier):
            sousartcl = lipanier.s_article
            article = sousartcl.article
            sousartcl.quantite += lipanier.quantite
            sousartcl.save()    
            article.quantite += lipanier.quantite
            article.save()
        instance.delete()


class CommandeClientUpdatedAPIView(generics.UpdateAPIView):
    serializer_class = CommandeClientForEmployeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CommandeClient.objects.all()
    
    def perform_update(self, serializer):
        employe = Employe.objects.get(user = self.request.user)
        serializer.save(livreur = employe)


class ArticleCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ArticleExpandedSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Article.objects.all()

class SousArticleCreateAPIView(generics.CreateAPIView):
    serializer_class = SousArticleSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


class UserGet(views.View):
    def get(self, request , *args , **kwargs):
        user = self.request.user
        data = UserSerializer(user, many=False).data
        return response.Response(data, status=status.HTTP_200_OK)


class SousArticleUpdateAPIView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = SousArticleSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = SousArticle.objects.all()

class SousArticleRetrieveAPIView(generics.RetrieveAPIView):
    lookup_field = 'id'
    serializer_class = SousArticleSerializer
    permission_classes = [IsAuthenticated]
    queryset = SousArticle.objects.all()

    def get(self, request , *args , **kwargs):
        query = self.get_object()
        data = self.serializer_class(data=query, many = False).data
        for item in data:
            item['nom'] = Article.objects.get(article=item['article']).nom
            item.pop('article')
            #item.pop('prev_prix')
            #item.pop('quantite')
        return data


class CaracteristiqueCreateAPIView(generics.CreateAPIView):
    serializer_class = CaracteristiqueSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


class CaracteristiqueUpdateAPIView(generics.RetrieveUpdateAPIView):
    lookup_field = 'id'
    serializer_class = CaracteristiqueSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]
    queryset = Caracteristique.objects.all()

class PromotManager:

    def applyorstop_promotion(self, article):
        promotion = Promotion.objects.filter(article = article, 
                                            debut_promotion__lt=datetime.now(), 
                                            fin_promotion__gt=datetime.now())
        if promotion.exists() and article.prev_prix_present is None:
            promotion = promotion.first()
            reduction = promotion.reduction
            article.prev_prix_present = article.prix_present
            article.prix_present -= article.prix_present * reduction
            sousartcls = SousArticle.objects.filter(article = article)
            for sa in sousartcls:
                sa.prev_prix = sa.prix
                sa.prix -= sa.prix * reduction
                sa.save()
            article.save()
            return True

        if not promotion.exists() and article.prev_prix_present is not None:
            article.prix_present = article.prev_prix_present
            article.prev_prix_present = None
            sousartcls = SousArticle.objects.filter(article = article)
            for sa in sousartcls:
                sa.prix = sa.prev_prix
                sa.prev_prix = None
                sa.save()
            article.save()
            return True
        return False





class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client
