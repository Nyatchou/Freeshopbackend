from rest_framework.test import APITestCase
from django.contrib.auth.admin import UserAdmin, User
from freeshop.models import *
from rest_framework.permissions import IsAdminUser, IsAuthenticated
#from rest_framework.reverse import reverse
from rest_framework import status
from django.db import models
from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
import os

class ArticleCreateTestCase(APITestCase):
    
    def setUp(self):    
        User.objects.create_superuser(username='Nyat', password='Franck23.') 
        self.categorie = Categorie.objects.create(nom='Shoes')
        self.souscateg = SousCategorie.objects.create(categorie=self.categorie, nom='Montante')
        file = File(open('../my_site/media/accessoire.png', 'rb'))
        uploaded_file = SimpleUploadedFile('accessoire0.png', file.read(), content_type='image/png')
        self.article1 = Article.objects.create(nom="bask", description="jolie", prix_present=11200,  image_present=uploaded_file,  sous_categorie=self.souscateg)
        self.article2 = Article.objects.create(nom="sliper", description="aimable et appreciable", image_present=uploaded_file, prix_present=12000, sous_categorie=self.souscateg)
        self.sousarti = SousArticle.objects.create(article=self.article1, prix=10000, quantite=20)

    def test_get_categorie_list(self):
        data = {}
        url = api_reverse('categs-list')
        response = self.client.get(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # def test_create_objects(self):
    #     file = File(open('../my_site/media/accessoire.png', 'rb'))
    #     uploaded_file = SimpleUploadedFile('accessoire0.png', file.read(), content_type='image/png')
    #     data = {
    #             'nom':'basket', 
    #             'description':'belle chaussure', 
    #             'prix_present':12000, 
    #             'image_present': uploaded_file,
    #             'sous_categorie': self.souscateg.id, 
    #             }
    #     url = api_reverse('article-create')
    #     self.client.login(username='Nyat', password='Franck23.')
    #     response = self.client.post(url, data=data, format='multipart')
    
    #     article = response.data
    #     print(article)
    #     data_sa1 = {
    #         'article':article['id'],
    #         'prix':15000,
    #         'quantite':5,
    #     }
    #     data_sa2 = {
    #         'article':article['id'],
    #         'prix':12000,
    #         'quantite':4,
                
    #     }

    #     data_san = {
    #         'article':article['id'],
    #         'prix':10000,
    #         'quantite':2,
    #     }
    #     urlsa = api_reverse('sousarticle-create')
        

    #     res1 = self.client.post(urlsa, data=data_sa1)
    #     res2 = self.client.post(urlsa, data=data_sa2)

    #     self.client.put(api_reverse('sousarticle-update', kwargs = {'id': res1.data['pk']}), data=data_san)


    #     datac1 = {
    #         's_article':res1.data['pk'],
    #         'caracteristique':'Taille',
    #         'valeur':'42'
    #     }
    #     datac2 = {
    #         's_article':res1.data['pk'],
    #         'caracteristique':'couleur',
    #         'valeur':'bleue'
    #     }

    #     datac3 = {
    #         's_article':res2.data['pk'],
    #         'caracteristique':'couleur',
    #         'valeur':'bleue'
    #     }

    #     datac4 = {
    #         's_article':res2.data['pk'],
    #         'caracteristique':'taille',
    #         'valeur':'44'
    #     }

    #     datac5 = {
    #         's_article':res1.data['pk'],
    #         'caracteristique':'fabriquant',
    #         'valeur':'PUMA'
    #     }

    #     res_caract1 = self.client.post(api_reverse('caract-create'), data=datac1)
    #     self.client.post(api_reverse('caract-create'), data=datac2)
    #     self.client.post(api_reverse('caract-create'), data=datac3)
    #     self.client.post(api_reverse('caract-create'), data=datac5)

    #     self.client.put(api_reverse('caract-update', kwargs={'id':res_caract1.data['id']}), data=datac4)

    #     article_count = Article.objects.count()
    #     sousart_count = SousArticle.objects.count()
    #     carac_count = Caracteristique.objects.count()

    #     article = Article.objects.get(pk=response.data['id'])

    #     self.assertEqual(article_count, 3, 'article create failed')
    #     self.assertEqual(sousart_count, 2, 'sous article create failed')
    #     self.assertEqual(article.quantite, 6, "quantite pb")
    #     self.assertEqual(carac_count, 6, 'caracteristique create failed')
    #     self.assertEqual(article.prix_present, 10000, 'price update failed')

    #     caract1 = Caracteristique.objects.filter(s_article=res1.data['pk'])
    #     caract2 = Caracteristique.objects.filter(s_article=res2.data['pk'])

    #     self.assertEqual([caract1[0].caracteristique, caract1[1].caracteristique],[caract2[0].caracteristique, caract2[1].caracteristique], 'update caracta failed' )

    def test_get_articlessouscateg_list(self):
        url1 = api_reverse('articles-sc', kwargs = {"id":self.souscateg.pk})
        url2 = api_reverse('articles-sc2', kwargs = {"categorie":self.categorie.nom, "souscategorie":self.souscateg.nom} )
        response1 = self.client.get(url1, data={}, format='json')
        response2 = self.client.get(url2, data={}, format='json')

        self.assertEqual(response1.status_code, status.HTTP_200_OK, "failed get list articles by id sc")
        self.assertEqual(response2.status_code, status.HTTP_200_OK, "failed get list articles by namecateg and souscateg")

    
    # def test_get_article(self):
    #     file = File(open('../my_site/media/accessoire.png', 'rb'))
    #     uploaded_file = SimpleUploadedFile('accessoire0.png', file.read(), content_type='image/png')
    #     data = {
    #             'nom':'basket', 
    #             'description':'belle chaussure', 
    #             'prix_present':12000, 
    #             'image_present': uploaded_file,
    #             'sous_categorie': self.souscateg.id, 
    #             }
    #     url = api_reverse('article-create')
    #     self.client.login(username='Nyat', password='Franck23.')
    #     response = self.client.post(url, data=data, format='multipart')

    #     data_sa1 = {
    #         'article':response.data['id'],
    #         'prix':15000,
    #         'quantite':5,
    #     }
    #     urlsa = api_reverse('sousarticle-create')
    #     self.client.post(urlsa, data=data_sa1)
    #     url = api_reverse('article', kwargs={'id':response.data['id']})
    #     response = self.client.get(url, data={}, format='json')
    #     self.assertEqual(response.status_code, status.HTTP_200_OK, "failed get single article")
    #     self.assertIn('sousarticles', response.data, 'absence de sousarticle list')
        
    def tests_panier(self):
        self.client.login(username='Nyat', password='Franck23.')
        url = api_reverse('panier-create')
        id_user = User.objects.get(username='Nyat').id
        data = {
            'user': id_user,
            'total': 0
        }
        response = self.client.post(url, data=data)
        print(response.data['id'])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, 'Failed created panier')
        url_ligpanier = api_reverse('lignepanier-create')
        response2_1 = self.client.post(url_ligpanier, data={
            's_article': self.sousarti.id,
            'prixunitaire': self.sousarti.prix,
            'quantite': 5,
            'panier': response.data['id']
        })
        self.assertEqual(response2_1.status_code, status.HTTP_201_CREATED, 'Failed created lignepanier')

        print(response2_1.data)
        response2_2 = self.client.post(url_ligpanier, data={
            's_article': self.sousarti.id,
        })
        self.assertFalse((response2_2.status_code == status.HTTP_201_CREATED), 'error created lignepanier')

        url_panier = api_reverse('panier-datas')
        response_datas_panier = self.client.get(url_panier, data={}, format='json')
        self.assertEqual(response_datas_panier.status_code, status.HTTP_200_OK, 'error_get_panier')
        print(response_datas_panier.data)
        response_datas_panier_update = self.client.put(api_reverse('lignepanier', kwargs={'id': 1}), data={            
            's_article': self.sousarti.id,
            'quantite': 4,
            }, format='json')
        print(response_datas_panier_update.data)
        self.assertEqual(response_datas_panier_update.status_code, status.HTTP_200_OK, 'error_update_panier')
