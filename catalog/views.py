from django.shortcuts import render, redirect, get_object_or_404
from .models import Category, Products
from django.contrib.auth.decorators import login_required
from .forms import CategoryForm, ProductForm
from django.http import JsonResponse
from django.template.loader import render_to_string

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

#delete
@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category.delete()
    return redirect('category_list')


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

#add
@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm()
    return render(request, 'product/product_form.html', {'form': form})

#edit
@login_required
def edit_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('admin_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product/product_form.html', {'form': form, 'title': 'Edit Produk'})  

#delete
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'product/confirm_delete.html', {'product':product}) 
