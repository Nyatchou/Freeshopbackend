from django.contrib import admin
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
# Register your models here.
from .models import *

admin.site.register(Photo)
admin.site.register(Caracteristique)
admin.site.register(Promotion)
admin.site.register(VilleLivraison)
admin.site.register(PointLivraison)

class AdminURLMixin(object):
    def get_admin_url(self, obj):
        content_type=ContentType.objects.get_for_model(obj.__class__)
        return reverse("admin:freeshop_%s_change" % (content_type.model), args=(obj.id,))


class SousCategorieInline(admin.TabularInline):
    model=SousCategorie
    fieldsets = [
        (None, {'fields':['nom']})
    ]

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    inlines=[SousCategorieInline, ]

class CaracteristiqueInline(admin.TabularInline):
    model=Caracteristique
    fieldsets = [
        (None, {'fields':['caracteristique', 'valeur']})
    ]
    extra=0

class SousArticleInline(admin.TabularInline, AdminURLMixin):
    model=SousArticle
    readonly_fields =['sousarticle_link']
    fieldsets = [
        (None, {'fields':['sousarticle_link','prix', 'quantite']})
    ]
    def sousarticle_link(self, s_article):
        url =self.get_admin_url(s_article)
        return mark_safe("<a href='{}'>{}</a>".format(url, s_article.article.nom))
    extra=0

@admin.register(SousArticle)
class SousArticleAdmin(admin.ModelAdmin):
    inlines=[CaracteristiqueInline, ]
    readonly_fields = ['article']
    verbose_name='sous-article'

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    inlines=[SousArticleInline, ]
    search_fields = ['nom']
    list_filter=['nom', 'prix_present']
    

class CommandeClientInline(admin.TabularInline, AdminURLMixin):
    model=CommandeClient
    readonly_fields =['panier_link', 'livreur', 'totalpaye', 'date']
    fieldsets = [
        (None, {'fields':['panier_link', 'livreur', 'totalpaye', 'date']})
    ]
    def panier_link(self, panier):
        url =self.get_admin_url(panier)
        return mark_safe("<a href='{}'>{}</a>".format(url, panier.id))
    extra=0

class ArticleInline(admin.TabularInline, AdminURLMixin):
    model=Article
    readonly_fields =['article_link', 'fournisseur', 'sous_categorie']
    fieldsets = [
        (None, {'fields':['article_link', 'fournisseur', 'sous_categorie']})
    ]
    search_fields = ['nom']
    def article_link(self, article):
        url =self.get_admin_url(article)
        return mark_safe("<a href='{}'>{}</a>".format(url, article.nom))
    extra=0


# @admin.register(Abonne)
# class AbonneAdmin(admin.ModelAdmin):
#     inlines=[CommandeClientInline, ]
#     list_filter=['user']

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin, AdminURLMixin):
    model=Employe
    readonly_fields =['user_link']
    def user_link(self, user):
        url =self.get_admin_url(user)
        return mark_safe("<a href='{}'>{}</a>".format(url, user.username))
    extra=0

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    inlines=[ArticleInline, ]

@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    inlines=[ArticleInline, ]
    
@admin.register(LignePanier)
class LignePanierAdmin(admin.ModelAdmin, AdminURLMixin):
    readonly_fields = ['s_article', 'quantite', 'panier']
    fieldsets = [
        (None, {'fields':['s_article', 'quantite', 'panier']})
    ]
    def has_add_permission(self, request):
        return False

class LignePanierInline(admin.TabularInline, AdminURLMixin):
    model=LignePanier
    readonly_fields = ['s_article', 'quantite', 'panier']
    fieldsets = [
        (None, {'fields':['s_article', 'quantite', 'panier']})
    ]
    extra=0

@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    readonly_fields=['total']  
    inlines=[LignePanierInline, ]
    def has_add_permission(self, request):
        return False



@admin.register(CommandeClient)
class CommandeClientAdmin(admin.ModelAdmin):
    readonly_fields = ['abonne', 'panier', 'date', 'mode_livraison', 'frais_livraison', 'totalpaye', 'lieu_livraison', 'mode_paiement']
    def has_add_permission(self, request):
        return False

admin.site.register(ArticleToHome)

class ArticleToHomeInline(admin.TabularInline, AdminURLMixin):
    model=ArticleToHome
    # readonly_fields =['article']
    fieldsets = [
        (None, {'fields':['article']})
    ]
    # def article_link(self, articletohome):
    #     url =self.get_admin_url(articletohome)
    #     return mark_safe("<a href='{}'>{}</a>".format(url, articletohome.article.nom))
    extra=0

@admin.register(CategToHome)
class CategorieToHomeAdmin(admin.ModelAdmin):
    inlines=[ArticleToHomeInline, ]



