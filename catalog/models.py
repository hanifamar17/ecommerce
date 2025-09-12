from django.db import models
import os

#Kategori produk
class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

#gambar utama produk (simpan ke products/<pk>/main/<filename>)
def product_main_image_path(instance, filename):
    return os.path.join("products", "main", filename)

#gambar gallery produk (simpan ke products/<pk>/gallery/<filename>)
def product_gallery_path(instance, filename):
    return os.path.join("products", "gallery", filename)

#Produk
class Products(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image = models.ImageField(upload_to=product_main_image_path, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
#Gambar galeri produk
class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE, related_name='gallery')
    image = models.ImageField(upload_to=product_gallery_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.product.name}'