from django.shortcuts import render
from catalog.models import Products, Category
from django.core.paginator import Paginator

# LANDING PAGE
def landing_page(request):
    latest_products = Products.objects.order_by('-created_at')[:6]  # Ambil 6 produk terbaru

    return render(request, 'store/landing_page.html', {'latest_products': latest_products})

# semua produk
def all_products(request):
    products = Products.objects.all()
    categories = Category.objects.all()

    q = request.GET.get("q")
    if q:
        products = products.filter(name__icontains=q)

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    sort = request.GET.get("sort")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "latest":
        products = products.order_by("-created_at")

    return render(request, "store/products.html", {
        "products": products,
        "categories": categories
    })