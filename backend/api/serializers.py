from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.constants import MIN_COOKING_TIME, MAX_COOKING_TIME
from recipes.models import (
    Recipe,
    Ingredient,
    RecipeIngredient
)
from recipes.serializers import (
    RecipeMinifiedSerializer,
    IngredientInRecipeSerializer,
    RecipeIngredientCreateSerializer
)
from users.serializers import CustomUserSerializer


class UserWithRecipesSerializer(CustomUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count'
        )

    def get_recipes(self, obj):
        request = self.context['request']
        limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        return RecipeMinifiedSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()


class RecipeListSerializer(serializers.ModelSerializer):
    author = CustomUserSerializer(read_only=True)
    ingredients = IngredientInRecipeSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.favorites.filter(recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return user.shopping_cart.filter(recipe=obj).exists()


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    cooking_time = serializers.IntegerField(
        min_value=MIN_COOKING_TIME,
        max_value=MAX_COOKING_TIME
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'author',
            'name',
            'image',
            'text',
            'ingredients',
            'cooking_time',
        )

    @staticmethod
    def validate_ingredients(value):
        if not value:
            raise serializers.ValidationError(
                {'ingredients': 'Нужно добавить хотя бы один ингредиент.'}
            )
        ids = [item['id'] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError(
                {'ingredients': 'Ингредиенты не должны дублироваться.'}
            )
        missing = []
        for ingr in value:
            if not Ingredient.objects.filter(id=ingr['id']).exists():
                missing.append(ingr['id'])
        if missing:
            raise serializers.ValidationError(
                {'ingredients': f'Ингредиент(ы) с id={missing} не найден(ы).'}
            )
        return value

    def validate(self, attrs):
        request = self.context['request']
        method = request.method

        if method in ['POST', 'PATCH', 'PUT']:
            if ('image' not in self.initial_data
                    or not self.initial_data.get('image')):
                raise serializers.ValidationError(
                    {'image': 'Это поле обязательно.'}
                )
            if ('ingredients' not in self.initial_data
                    or not self.initial_data.get('ingredients')):
                raise serializers.ValidationError(
                    {'ingredients': 'Это поле обязательно.'}
                )
        return attrs

    @staticmethod
    def create_ingredients(recipe, ingredients_data):
        objs = [
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingr['id'],
                amount=ingr['amount']
            )
            for ingr in ingredients_data
        ]
        RecipeIngredient.objects.bulk_create(objs)

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        user = self.context['request'].user
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            new_ingredients = validated_data.pop('ingredients')
            instance.recipe_ingredients.all().delete()
            self.create_ingredients(instance, new_ingredients)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        return RecipeListSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        ).data
