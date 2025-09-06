from django.shortcuts import render, get_object_or_404
from catalog.models import Products, Category
from django.core.paginator import Paginator
from django.db.models import Q, Case, When, IntegerField, Sum
from django.http import JsonResponse

#LANDING PAGE
def landing_page(request):
    latest_products = Products.objects.order_by('-created_at')[:6]  # Ambil 6 produk terbaru

    return render(request, 'store/landing_page.html', {'latest_products': latest_products})

#search produk
def search_products(queryset, q):
    keywords = q.split()
    combined_query = Q()
    rank_expression = None

    for word in keywords:
        # filter query: produk cocok jika ada di name atau description
        combined_query |= Q(name__icontains=word) | Q(description__icontains=word)

        # rank +1 kalau name cocok
        case_name = Case(
            When(name__icontains=word, then=1),
            default=0,
            output_field=IntegerField()
        )

        # rank +1 kalau description cocok
        case_desc = Case(
            When(description__icontains=word, then=1),
            default=0,
            output_field=IntegerField()
        )

        # gabungkan ke rank_expression
        if rank_expression is None:
            rank_expression = case_name + case_desc
        else:
            rank_expression = rank_expression + case_name + case_desc

    if rank_expression is None:
        # tidak ada kata kunci → return queryset tanpa filter
        return queryset

    queryset = (
        queryset.filter(combined_query)
        .annotate(match_count=rank_expression)   # jumlah kata yang cocok
        .order_by("-match_count", "name")        # urutkan berdasarkan relevansi
    )

    return queryset

# semua produk
def all_products(request):
    products = Products.objects.all()
    categories = Category.objects.all()
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    q = request.GET.get("q")
    if q:
        products = search_products(products, q)

    # filter berdasarkan kategori
    category_ids = [c for c in request.GET.getlist("categories") if c]
    selected_categories = []
    selected_category_objs = []
    if category_ids:
        products = products.filter(category_id__in=category_ids)
        selected_categories = list(map(int, category_ids))
        selected_category_objs = Category.objects.filter(id__in=selected_categories)

    sort = request.GET.get("sort")
    if sort == "price_asc":
        products = products.order_by("price")
    elif sort == "price_desc":
        products = products.order_by("-price")
    elif sort == "latest":
        products = products.order_by("-created_at")

    return render(request, "store/products.html", {
        "products": products,
        "categories": categories,
        "selected_categories": selected_categories,
        "selected_category_objs": selected_category_objs,
        "cart_count": cart_count,
    })

#detail produk
def product_detail(request, pk):
    product = get_object_or_404(Products, pk=pk)
    category = Category.objects.all()

    return render(request, 'store/product_detail.html', {'product': product, 'categories': category})

#tambah ke keranjang
def add_to_cart(request, pk):    
    if request.method == "POST":
        product = get_object_or_404(Products, pk=pk)

        # cek stok
        if product.stock <= 0:
            return JsonResponse({
                "status": "error",
                "message": "Stok produk tidak mencukupi."
            }, status=400)

        # ambil keranjang dari session
        cart = request.session.get("cart", {})

        # tambah/update produk di cart
        if str(product.id) in cart:
            cart[str(product.id)]["quantity"] += 1
        else:
            cart[str(product.id)] = {
                "name": product.name,
                "price": float(product.price),
                "quantity": 1,
                "image_url": product.image.url if product.image else ""
            }

        # kurangi stok produk
        product.stock -= 1
        product.save()

        # simpan ke session
        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({
            "status": "success",
            "message": f"{product.name} berhasil ditambahkan ke keranjang!"
        })

    return JsonResponse({
        "status": "error",
        "message": "Metode tidak valid!"
    }, status=405)



#keranjang belanja
def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    cart_count = sum(item["quantity"] for item in cart.values())
    
    total = 0 
    for key, item in cart.items():
        subtotal = item["price"] * item["quantity"] 
        total += subtotal

        cart_items.append({
            "id": key,
            "name": item["name"],
            "price": item["price"],
            "quantity": item["quantity"],
            "image_url": item.get("image_url", ""),
            "subtotal": subtotal
        })

    return render(request, 'store/cart.html', {'cart_items': cart_items, 'cart_count': cart_count, 'total': total})