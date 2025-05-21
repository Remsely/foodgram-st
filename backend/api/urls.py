from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views.ingridients import IngredientViewSet
from .views.recipes import RecipeViewSet
from .views.users import CustomUserViewSet

router = DefaultRouter()
router.register(
    r'users',
    CustomUserViewSet,
    basename='users'
)
router.register(
    r'recipes',
    RecipeViewSet,
    basename='recipes'
)
router.register(
    r'ingredients',
    IngredientViewSet,
    basename='ingredients'
)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
