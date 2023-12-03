from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('home/', views.home, name='home'),
    path('unit/', views.unit, name='unit'),
    path('admins/', views.admins, name='admins'),
    path('creacc/', views.creacc, name='creacc'),
    path('ad_hom/', views.ad_hom, name='ad_hom'),
    path('ad_tent/', views.ad_tent, name='ad_tent'),
    path('tnt_hom/', views.tnt_hom, name='tnt_hom'),
    path('contact/', views.contact, name='contact'),
    path('vtour/', views.vtour, name='vtour'),
    path('amnts/', views.amnts, name='amnts'),
    path('book/', views.book, name='book'),
    path('comp/', views.comp, name='comp'),
    path('req/', views.req, name='req'),
    path('nav/', views.nav, name='nav'),
    path('prop/', views.prop, name='prop'),
    path('rep/', views.rep, name='rep'),
    path('foot/', views.foot, name='foot'),
    path('bookpay/', views.bookpay, name='bookpay'),

    path('pay/<str:username>/', views.pay, name='pay'),
    path('delete-tent/<int:tenant_id>/', views.delete_tent, name='delete-tent'),
    path('delete-unit/<int:unit_id>/', views.delete_unit, name='delete_unit'),
    path('comp_solv/<int:issue_id>/', views.comp_solv, name='comp_solv'),
    path('', views.index, name='index'),
    path('logout/', views.user_logout, name='logout'),
]