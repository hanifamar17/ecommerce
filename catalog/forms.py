from django import forms
from .models import Category, Products

#Form untuk kategori produk
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Masukkan nama kategori...',
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
                'required': 'required',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,  # tinggi textarea
                'placeholder': 'Masukkan deskripsi kategori...',
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
            }),
        }

#Form untuk produk
class ProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price', 'stock', 'image', 'category']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Masukkan nama produk...',
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
                'required': 'required',
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Masukkan deskripsi produk...',
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200 resize-none',
            }),
            'price': forms.NumberInput(attrs={
                'class': 'w-full text-sm pl-10 pr-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
                'min': '0',
                'required': 'required',
            }),
            'stock': forms.NumberInput(attrs={
                'placeholder': 'Masukkan jumlah stok...',
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
                'min': '0',
                'required': 'required',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full text-sm px-4 py-3 rounded-lg border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all duration-200',
                'required': 'required',
            }),
        }