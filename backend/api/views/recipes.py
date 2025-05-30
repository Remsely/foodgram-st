from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import (
    Recipe,
    RecipeIngredient
)
from recipes.serializers import (
    RecipeShortLinkSerializer,
    RecipeMinifiedSerializer
)
from ..filters import RecipeFilter
from ..permissions import IsAuthorOrReadOnly
from ..serializers import RecipeCreateUpdateSerializer, RecipeListSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'get_link'):
            return [permissions.AllowAny()]
        if self.action in (
                'create',
                'favorite',
                'shopping_cart',
                'download_shopping_cart'):
            return [permissions.IsAuthenticated()]

        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

    def get_serializer_class(self):
        if self.action in ['create', 'partial_update']:
            return RecipeCreateUpdateSerializer
        return RecipeListSerializer

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[permissions.AllowAny],
        url_path='get-link',
    )
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = RecipeShortLinkSerializer(
            recipe,
            context={
                'request': request
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.shopping_cart.create(recipe=recipe)
            serializer = RecipeMinifiedSerializer(
                recipe,
                context={
                    'request': request
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart_item = user.shopping_cart.filter(recipe=recipe).first()
            if not cart_item:
                return Response(
                    {'errors': 'Рецепта нет в списке покупок.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart_item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        user = request.user
        ingredients_qs = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(total_amount=Sum('amount'))

        if not ingredients_qs.exists():
            content = 'Ваш список покупок пуст.\n'
        else:
            lines = []
            for item in ingredients_qs:
                name = item['ingredient__name']
                unit = item['ingredient__measurement_unit']
                total = item['total_amount']
                lines.append(f"{name} ({unit}) — {total}")
            content = "\n".join(lines)

        response = HttpResponse(
            content,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[permissions.IsAuthenticated],
        url_path='favorite',
    )
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.favorites.create(recipe=recipe)
            serializer = RecipeMinifiedSerializer(
                recipe,
                context={
                    'request': request
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        fav_item = user.favorites.filter(recipe=recipe).first()
        if not fav_item:
            return Response(
                {'errors': 'Рецепта нет в избранном.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        fav_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
