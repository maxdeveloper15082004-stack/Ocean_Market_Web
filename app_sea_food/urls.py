from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    
    path('product/<path:product_slug>/', views.product_detail, name='product_detail'),
    
    path('cart/', views.cart, name='cart'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-cart/<int:cart_item_id>/', views.update_cart, name='update_cart'),
    
    path('wishlist/', views.wishlist, name='wishlist'),
    path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:wishlist_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    
    path('orders/', views.orders, name='orders'),
    path('order/<str:order_number>/', views.order_detail, name='order_detail'),
    
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/add-product/', views.add_product, name='add_product'),
    path('admin/edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('admin/delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/update-order/<str:order_number>/', views.update_order_status, name='update_order_status'),
]
