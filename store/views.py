from django.shortcuts import render, get_object_or_404, redirect
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
    cart = request.session.get("cart", {})
    cart_count = sum(item["quantity"] for item in cart.values())

    return render(request, 'store/product_detail.html', {'product': product, 'categories': category, 'cart_count': cart_count})

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

        cart_count = sum(item["quantity"] for item in cart.values())

        return JsonResponse({
            "status": "success",
            "message": f"{product.name} berhasil ditambahkan ke keranjang!",
            "cart_count": cart_count
        })

    return JsonResponse({
        "status": "error",
        "message": "Metode tidak valid!"
    }, status=405)

#keranjang belanja
def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0
    updated_cart = {}
    
    notification_message = None

    for product_id, item_data in cart.items():
        try:
            # Menggunakan get() daripada get_object_or_404()
            # agar kita bisa menangani sendiri kasus ketika produk tidak ditemukan
            product = Products.objects.get(pk=product_id)
            
            # Perbarui data item di keranjang dengan informasi terbaru dari database
            item_data["name"] = product.name
            item_data["price"] = float(product.price)
            item_data["image_url"] = product.image.url if product.image else ""

            subtotal = item_data["price"] * item_data["quantity"]
            total += subtotal

            cart_items.append({
                "id": product_id,
                "name": item_data["name"],
                "price": item_data["price"],
                "quantity": item_data["quantity"],
                "image_url": item_data["image_url"],
                "subtotal": subtotal
            })

            updated_cart[str(product.id)] = item_data
        
        except Products.DoesNotExist:
            # Jika produk tidak ditemukan, siapkan pesan notifikasi
            notification_message = "Keranjang diperbarui: beberapa produk telah dihapus."
            print(f"Produk dengan ID {product_id} tidak ditemukan. Menghapus dari keranjang.")
    
    # Sinkronkan keranjang di session dengan data yang valid
    if notification_message:
        request.session["cart"] = updated_cart
        request.session.modified = True
    
    cart_count = sum(item["quantity"] for item in updated_cart.values())

    context = {
        'cart_items': cart_items,
        'cart_count': cart_count,
        'total': total,
        'notification': notification_message, # Tambahkan pesan notifikasi ke konteks
    }

    return render(request, 'store/cart.html', context)

#update cart
def update_cart(request):
    if request.method == 'POST':
        product_id = str(request.POST.get("product_id"))
        action = request.POST.get("action")

        cart = request.session.get("cart", {})
        product = get_object_or_404(Products, pk=product_id)
        
        if product_id not in cart:
            return JsonResponse({"status": "success", "message": "Produk tidak ada di keranjang" })
        
        if action == "increase":
            if product.stock > 0:
                cart[product_id]["quantity"] += 1
                product.stock -= 1
                product.save()
                message = f"Stok {product.name} bertambah."
            else:
                return JsonResponse({"status": "error", "message": "Stok habis!"})
        elif action == "decrease":
            cart[product_id]["quantity"] -= 1
            product.stock += 1
            product.save()

            if cart[product_id]["quantity"] <= 0:
                del cart[product_id]
                message = f"{product.name} dihapus dari keranjang."
            else:
                message = f"Stok {product.name} dikurangi."
            
        request.session["cart"] = cart
        return JsonResponse({"status": "success", "message": message})
    
    return JsonResponse({"status": "success", "message": "Metode tidak valid"})