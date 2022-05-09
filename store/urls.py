from django.urls import path, include
from rest_framework_nested import routers

from . import views

router = routers.DefaultRouter()
router.register('products', views.ProductViewset, basename='products')
router.register('collections', views.CollectionViewset)
router.register('carts', views.CartViewset)

product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewset,
                        basename='product-reviews')

cart_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
cart_router.register('items', views.CartitemViewset, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_router.urls))
    # path('', views.StoreView.as_view()),
    # path('product/<int:id>/', views.ProductView.as_view()),
    # path('collection/', views.CollectionView.as_view()),
    # path('collection/<int:pk>/', views.CollectionDetail.as_view(), name= 'collection_detail')
]
