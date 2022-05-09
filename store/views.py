from django.shortcuts import get_object_or_404
from django.db.models import Count
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import CartItem, OrderItem, Product, Collection, Review, Cart
from .serializer import AddCartitemSerializer, CartItemSerializer, ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, UpdateCartitemserializer
from .filters import ProductFilter
from .pagination import DefaultPagination

# Create your views here.


class ProductViewset(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({
                'error': 'Product cannot be deleted'},
                status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class CollectionViewset(ModelViewSet):
    queryset = Collection.objects.annotate(
        products_count=Count('product')).all()
    serializer_class = CollectionSerializer

    def destroy(self, request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.product_set.count() > 0:
            return Response({
                'error': 'can not be deleted'
            }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)


class ReviewViewset(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewset(CreateModelMixin,
                  RetrieveModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer


class CartitemViewset(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartitemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartitemserializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects \
            .filter(cart_id=self.kwargs['cart_pk']) \
            .select_related('product')

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

# ----------------------------------------------------------
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView


# class StoreView(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return self.request


# class ProductView(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitem_set.count() > 0:
#             return Response({
#                 'error': 'Product cannot be deleted'},
#                             status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# class CollectionView(ListCreateAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('product')).all()
#     serializer_class = CollectionSerializer

#     def get_serializer_context(self):
#         return self.request


# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(products_count=Count('product'))
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk,*args, **kwargs):
#         collection = get_object_or_404(Collection, pk=pk)
#         if collection.product_set.count() > 0:
#             return Response({
#                 'error': 'can not be deleted'
#             }, status=status.HTTP_405_METHOD_NOT_ALLOWED)

#         collection.delete()
#         return Response(status=status.HTTP_404_NOT_FOUND)
