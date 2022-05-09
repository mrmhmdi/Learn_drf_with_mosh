from rest_framework import serializers
from decimal import Decimal

from .models import Collection, Product, Review, Cart, CartItem


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Collection
        fields = ['id', 'title', 'products_count']


class ProductSerializer(serializers.ModelSerializer):
    price_tax = serializers.SerializerMethodField(method_name='tax_calculate')

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug',
                  'inventory', 'unit_price', 'price_tax', 'collection']

    def tax_calculate(self, product: Product):

        return product.unit_price * Decimal(1.1)


class ReviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Review
        fields = ['id', 'name', 'description']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)


class SimpleProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

    def get_total_price(self, cartitem: Cart):
        return cartitem.quantity * cartitem.product.unit_price


class AddCartitemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('no product with this id')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        print(self)
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item

        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, product_id=product_id, quantity=quantity)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']


class UpdateCartitemserializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        quantity = self.validated_data['quantity']
        self.instance.quantity += quantity
        self.instance.save()
        return self.instance

    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'created_at', 'items', 'total_price']

    def get_total_price(self, cart):
        return sum([item.quantity*item.product.unit_price for item in cart.items.all()])
