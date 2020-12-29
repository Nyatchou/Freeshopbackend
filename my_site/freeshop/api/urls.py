from django.urls import path

from freeshop.api.views import *

urlpatterns = [
    path('categshome/', HomeView.as_view(), name='home-categs'),
    path('categories/', CategorieListAPIView.as_view(), name='categs-list'),
    path('souscategorie/<int:id>', ArticlesSousCategorieView.as_view(), name='articles-sc'),
    path('articleslist/<int:id_sc>', ArticlesListAPIView.as_view(), name='articles-sc2'),
    path('article/<int:id>', ArticleRetrieveAPIView.as_view(), name='article'),
    path('panier/<int:id>', PanierRUAPIView.as_view(), name='panier'),
    path('panier/', LignesPanierListView.as_view(), name='panier-datas'),
    path('panier/create/', PanierCreateAPIView.as_view(), name = 'panier-create'),
    path('lignepanier/<int:id>', LignePanierRUDAPIView.as_view(), name='lignepanier'),
    path('lignepanier/create/', LignePanierCreateAPIView.as_view(), name='lignepanier-create'),
    path('commandeclient/create/', CommandeClientCreateAPIView.as_view(), name='commandeclient-create'),
    path('commandeclient/delete/<int:id>', CommandeClientRDAPIView.as_view(), name='commandeclient-rd'),
    path('articles/create/', ArticleCreateAPIView.as_view(), name='article-create'),
    path('sousarticle/create/', SousArticleCreateAPIView.as_view(), name='sousarticle-create'),
    path('caract/create/', CaracteristiqueCreateAPIView.as_view(), name='caract-create'),
    path('sousarticles/<int:id>', SousArticleRetrieveAPIView.as_view(), name='sousarticle-read'),
    path('sousarticle/update/<int:id>', SousArticleUpdateAPIView.as_view(), name='sousarticle-update'),
    path('caract/update/<int:id>', CaracteristiqueUpdateAPIView.as_view(), name='caract-update'),
    path('user/', UserGet.as_view(), name='user-get'),
    path('categorie/<str:categorie>/<str:souscategorie>', ArticlesSousCategorieAPIView.as_view(), name='articles-sc2'),
]