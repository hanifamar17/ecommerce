from django.shortcuts import render, redirect, get_object_or_404
from .models import Products
from django.contrib.auth.decorators import login_required
from .forms import ProductForm

# Create your views here.
@login_required
def admin_dashboard(request):
    product= Products.objects.all()
    return render(request, 'admin/dashboard.html', {'products': product})

#CRUD PRODUCT
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
    return render(request, 'admin/product_form.html', {'form': form})

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
    return render(request, 'admin/product_form.html', {'form': form, 'title': 'Edit Produk'})  

#delete
@login_required
def delete_product(request, pk):
    product = get_object_or_404(Products, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('admin_dashboard')
    return render(request, 'admin/confirm_delete.html', {'product':product}) 
