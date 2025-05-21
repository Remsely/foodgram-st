from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from recipes.models import Ingredient
from recipes.serializers import IngredientSerializer
from ..filters import IngredientFilter


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None
