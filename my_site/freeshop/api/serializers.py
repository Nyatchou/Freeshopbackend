from rest_framework import serializers
from freeshop.models import *
from django.contrib.auth.models import User

class ArticleSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Article
        fields = [
            'pk',
            'nom',
            'url',
            'image_present',
            'prev_prix_present',
            'prix_present',
            'quantite'
        ]

    def get_url(self, obj):
        request = self.context.get('request')
        return obj.get_api_url(request=request)

class CaracteristiqueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Caracteristique
        exclude = ['id']

    def create(self, validated_data):
        caract = Caracteristique.objects.create(**validated_data)
        article = caract.s_article.article
        id_sousarticl =caract.s_article.id
        for sa in SousArticle.objects.filter(article=article):
            if sa.id is not id_sousarticl:
                Caracteristique.objects.create(caracteristique=validated_data['caracteristique'], valeur='', s_article=sa)
        return caract

    def update(self, instance, validated_data):
        article = instance.s_article.article
        instance.valeur = validated_data.get('valeur', instance.valeur)
        prev_caract = instance.caracteristique
        val_caract = validated_data.get('caracteristique', instance.caracteristique)
        instance.caracteristique = val_caract
        instance.save()
        if prev_caract is not val_caract:
            for sousarticle in SousArticle.objects.filter(article=article):
                if instance.s_article.id != sousarticle.id:
                    try:
                        caract = Caracteristique.objects.get(s_article=sousarticle, caracteristique=prev_caract)
                        caract.caracteristique = val_caract
                        caract.save()
                    except:
                        Caracteristique.objects.create(s_article=sousarticle, caracteristique= val_caract, valeur="")
        return instance

    def validate_caracteristique(self, value):
        qs = Caracteristique.objects.filter(s_article = self.initial_data['s_article'], caracteristique=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("Cette caractéristique existe déjà pour cet élément")
        return value


    

class SousArticleSerializer(serializers.ModelSerializer):
    caracteristiques = CaracteristiqueSerializer(many=True, read_only=True)
    class Meta:
        model = SousArticle
        fields = [
            'pk', 
            'article', 
            'prev_prix', 
            'prix', 
            'quantite', 
            'caracteristiques'
            ]
        read_only_fields = ['prev_prix']

    def create(self, validated_data):
        sousarticle = SousArticle.objects.create(**validated_data)
        article = sousarticle.article
        neignb_sousartcls = SousArticle.objects.filter(article=article).exclude(pk=sousarticle.pk)  
        if neignb_sousartcls.exists():
            item = neignb_sousartcls.first()
            caracts_item = Caracteristique.objects.filter(s_article=item)
            for caract in caracts_item:    
                Caracteristique.objects.create(s_article=sousarticle, caracteristique=caract.caracteristique, valeur="")
        article = self.set_articleprice(article) 
        article.quantite += sousarticle.quantite
        article.save()
        return sousarticle


    def update(self, instance, validated_data):
        article = instance.article
        if instance.quantite != validated_data.get('quantite', instance.quantite):
            passed_qte = instance.quantite
            instance.quantite = validated_data.get('quantite', instance.quantite)
            article.quantite = article.quantite - passed_qte + validated_data.get('quantite')
        instance.prix = validated_data.get('prix', instance.prix)
        instance.save()
        article = self.set_articleprice(article)
        article.save()
        return instance

    def set_articleprice(self, article):
        prix_and_prevprix = SousArticle.objects.filter(article = article).values_list('prix', 'prev_prix').order_by('prix').first()
        article.prix_present = prix_and_prevprix[0]
        article.prev_prix_present = prix_and_prevprix[1]
        return article


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['photo']

class ArticleExpandedSerializer(serializers.ModelSerializer):
    sousarticles = SousArticleSerializer(many=True, read_only=True)
    photos = PhotoSerializer(many=True, read_only=True)
    class Meta:
        model = Article
        exclude = ['fournisseur']
        read_only_fields = ['quantite']
    # def create(self, validated_data):
    #     print(validated_data)
    #     caracteristiques = validated_data.pop('sousarticles')['caracteristiques']
    #     article = Article.objects.create(**validated_data)
    #     sousarticle = SousArticle.objects.create(quantite=article.quantite, article=article, prix=article.prix_present, prev_prix=article.prev_prix_present)
    #     for caract in caracteristiques:
    #         Caracteristique.objects.create(s_article = sousarticle, **caract)
    #     return article

class SousCategorieSerializer(serializers.ModelSerializer):
    articles = ArticleSerializer(many=True, read_only=True)
    categorie = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = SousCategorie
        fields = ['pk','nom', 'categorie', 'articles']

    def get_categorie(self, obj):
        return obj.get_category_name()



class SimpleSousCategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = SousCategorie
        fields =  ['pk','nom']

class CategorieSerializer(serializers.ModelSerializer):
    souscategories = SimpleSousCategorieSerializer(many=True, read_only=True)
    class Meta:
        model = Categorie
        fields  = ['pk','nom', 'image', 'souscategories']

# class SimpleCategorieSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Categorie
#         fields = '__all__'

class LignePanierSerializer(serializers.ModelSerializer):
    class Meta:
        model = LignePanier
        fields = '__all__'
        read_only_fields = ['prixunitaire', 'panier']

    def create(self, validated_data):
        sousarticle = validated_data.get('s_article')
        try: 
            pan = validated_data.get('panier')
            print(pan.id)
            lignepanier = LignePanier.objects.create(**validated_data, prixunitaire=sousarticle.prix)
            panier = lignepanier.panier
            panier.total += lignepanier.prixunitaire * lignepanier.quantite
        except:
            panier = Panier.objects.get(user=self.context.get("request").user, statut='non finalisé')
            lignepanier = LignePanier.objects.create(**validated_data, prixunitaire=sousarticle.prix, panier=panier)
            panier.total += lignepanier.prixunitaire * lignepanier.quantite
        panier.save()
        return lignepanier

    def update(self, instance, validated_data):
        panier = instance.panier
        panier.total += instance.prixunitaire * (-instance.quantite + validated_data.get('quantite', instance.quantite))
        panier.save()
        #instance.prixunitaire = validated_data.get('prixunitaire', instance.prixunitaire)
        instance.quantite = validated_data.get('quantite', instance.quantite)
        #instance.s_article = validated_data.get('s_article', instance.s_article)
        instance.save()
        return instance

    def validate_s_article(self, value):
        panier = Panier.objects.get(user=self.context.get("request").user, statut='non finalisé')
        sousarticle = SousArticle.objects.get(pk = self.initial_data['s_article'])
        lignespanier = LignePanier.objects.filter(panier=panier, s_article=sousarticle)
        if self.instance:
            lignespanier = lignespanier.exclude(s_article=sousarticle)
        if lignespanier.exists():
            raise serializers.ValidationError("Cet élément fait déjà partie d'une ligne du panier")
        return value

    def validate_quantite(self, value):
        sousarticl = SousArticle.objects.get(pk = self.initial_data['s_article'])
        if sousarticl.quantite <= value:
            raise serializers.ValidationError("La quantite en stock est insuffisante pour satisfaire à votre demande")
        return value

class PanierSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    lignespanier = LignePanierSerializer(many=True, read_only=True)

    class Meta:
        model = Panier
        fields = '__all__'
        read_only_fields = []

    def get_url(self, obj):
        request = self.context.get("request")
        return obj.get_api_url(request=request)

    def validate_user(self, value):
        user = self.initial_data['user']
        paniers = Panier.objects.filter(user = user, statut='non finalisé')
        if self.instance:
            paniers = paniers.exclude(user = user)
        if paniers.exists():
            raise serializers.ValidationError("Vous ne pouvez pas créer un nouveau panier !")
        #print(value)
        return value


    # def create(self, validated_data):
    #     lignespanier_data = validated_data.pop('lignespanier')
    #     panier = Panier.objects.create(**validated_data)
    #     for lignepanier_data in lignespanier_data:
    #         LignePanier.objects.create(panier=panier, **lignepanier_data)
    #     return panier

class ArticleToHomeSerializer(serializers.ModelSerializer):
    article = ArticleSerializer(many=False, read_only=True)
    class Meta:
        model = ArticleToHome
        fields = ['article']
    
class CategToHomeSerializer(serializers.ModelSerializer):
    articlestohome = ArticleToHomeSerializer(many=True, read_only=True)
    class Meta:
        model = CategToHome
        exclude = ['id']


class CommandeClientForClientSerializer(serializers.ModelSerializer):
    abonnename = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CommandeClient
        exclude = ['livreur']
        read_only_fields = ['abonne']

    def get_abonnename(self, obj):
        abonne_name = obj.abonne.user.username
        return abonne_name

    def create(self, validated_data):
        commandeclient = CommandeClient.objects.create(**validated_data)
        panier = commandeclient.panier
        for lipanier in LignePanier.objects.filter(panier=panier):
            sousartcl = lipanier.s_article
            article = sousartcl.article
            sousartcl.quantite -= lipanier.quantite
            sousartcl.save()    
            article.quantite -= lipanier.quantite
            article.save()
        return commandeclient

    def validate_panier(self, value):
        panier = Panier.objects.get(pk=self.initial_data['panier'])
        for lipanier in LignePanier.objects.filter(panier=panier):
            sousartcl = lipanier.s_article
            article = sousartcl.article
            if sousartcl.quantite < lipanier.quantite:
                raise serializers.ValidationError("La quantite en stock de {} est insuffisante pour satisfaire à votre demande".format(article.nom))
        return value
        

class CommandeClientForEmployeSerializer(serializers.ModelSerializer):
    abonnename = serializers.SerializerMethodField(read_only=True)
    livreur_name = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = CommandeClient
        fields = ['abonnename' ,'pk', 'etat']
        read_only_fields = ['abonnename']

    def get_abonnename(self, obj):
        abonne_name = obj.abonne.user.username
        return abonne_name

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'