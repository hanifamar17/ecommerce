from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Products, ProductImage
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, ProductForm, ProductImageForm
from django.http import JsonResponse, HttpResponseBadRequest
from django.template.loader import render_to_string
import os
from django.conf import settings

# Create your views here.
@login_required
def admin_dashboard(request):
    return render(request, 'product/dashboard.html')


#CRUD CATEGORY
@login_required
def category_list(request):
    category = Category.objects.all()
    category_form = CategoryForm() 

    return render(request, 'product/category.html', {
        'categories': category,
        'category_form': category_form
        })

#add
@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)

        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Kategori berhasil ditambahkan.'})  
        else:  
            return JsonResponse({'status': 'error', 'message': 'Form tidak valid', 'errors': form.errors}, status=400)
    form = CategoryForm()
    return render(request, 'product/category_form.html', {'form': form})

#edit
@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': 'Kategori berhasil diperbarui.'})
        return JsonResponse({'status': 'error', 'message': 'Form tidak valid', 'errors': form.errors}, status=400)
    form = CategoryForm(instance=category)
    return render(request, 'product/category_form.html', {'form': form, 'category': category})

#confirm delete
@login_required
def confirm_delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    return render(request, "product/confirm_delete_category.html", {"category": category})

#delete
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Kategori berhasil dihapus.'})
        return redirect('category_list')
    return HttpResponseBadRequest('Invalid request method.')


#CRUD PRODUCT
@login_required
def product_list(request):
    product= Products.objects.all()
    category = Category.objects.all()
    product_form = ProductForm()
    category_form = CategoryForm()   

    return render(request, 'product/product.html', {
        'products': product,
        'categories': category,
        'product_form': product_form,
        'category_form': category_form
        })

#detail produk
@login_required
def detail_product(request, pk):
    product = get_object_or_404(Products, pk=pk)

    return render(request, 'product/detail_product.html', {'product': product})

#add
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)

        if form.is_valid():
            product = form.save(commit=False)

            #gambar utama
            if "image" in request.FILES:
                product.image = request.FILES["image"]
                product.save()

            #galeri produk
            for img in request.FILES.getlist('gallery_images'):
                ProductImage.objects.create(product=product, image=img)
                
            return JsonResponse({'status': 'success', 'message': 'Produk berhasil ditambahkan.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Form tidak valid', 'errors': form.errors}, status=400)
    else:
        form = ProductForm()
    return render(request, 'product/product_form.html', {'form': form})

#edit
@login_required
# edit
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    
    old_main_image_path = product.image.path if product.image else None
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)

        if form.is_valid():
            # Handle main product image update
            if 'image' in request.FILES:
                if old_main_image_path and os.path.exists(old_main_image_path):
                    os.remove(old_main_image_path)
                
                product.image = request.FILES['image']
            
            product.save()

            # Handle gallery images update
            if 'gallery_images' in request.FILES:
                # Delete old gallery images from disk
                for gallery_item in product.gallery.all():
                    if gallery_item.image and os.path.exists(gallery_item.image.path):
                        os.remove(gallery_item.image.path)
                
                # Delete records from the database
                product.gallery.all().delete()
                
                # Save new gallery images
                for img in request.FILES.getlist('gallery_images'):
                    ProductImage.objects.create(product=product, image=img)

            return JsonResponse({'status': 'success', 'message': 'Produk berhasil diperbarui.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Form tidak valid', 'errors': form.errors}, status=400)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'product/product_form.html', {'form': form, 'title': 'Edit Produk'})

#confirm delete
@login_required
def confirm_delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    return render(request, "product/confirm_delete_product.html", {"product": product})

#delete
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)

    if request.method == 'POST':
        product.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Produk berhasil dihapus.'})
        return redirect('product_list')
    return HttpResponseBadRequest('Invalid request method.') 

#delete image from gallery
@login_required
def delete_product_image(request, pk):
    image = get_object_or_404(ProductImage, pk=pk)
    product_id = image.product.pk

    if request.method == "POST":
        image.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': 'Gambar berhasil dihapus.'})
        return redirect('edit_product', pk=product_id)

    return HttpResponseBadRequest('Invalid request method.')

