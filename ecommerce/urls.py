"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from catalog import views
from store import views as store_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),

    #crud category
    path('categories/', views.category_list, name='category_list'),
    path('category/add/', views.add_category, name='add_category'),
    path('category/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('category/confirm-delete/<int:pk>/', views.confirm_delete_category, name='confirm_delete_category'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),

    #crud product
    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.detail_product, name='detail_product'),
    path('product/add/', views.add_product, name='add_product'),
    path('product/edit/<int:pk>/', views.edit_product, name='edit_product'),
    path('product/confirm-delete/<int:pk>/', views.confirm_delete_product, name='confirm_delete_product'),
    path('product/delete/<int:pk>/', views.delete_product, name='delete_product'),

    #STORE SECTION
    path('', store_views.landing_page, name='landing_page'),
    path('store/products/', store_views.all_products, name='all_products'),
    path('store/product/<int:pk>/', store_views.product_detail, name='product_detail'),
    path('store/add-to-cart/<int:pk>/', store_views.add_to_cart, name='add_to_cart'),
    path('store/cart/', store_views.cart_view, name='cart_view'),
    path('store/cart/update/', store_views.update_cart, name='update_cart'),
    path('store/cart/checkout/', store_views.cart_checkout, name='cart_checkout'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)