from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """Test publicly available Ingredients API"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required for retrieving ingredients list"""

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """Test the authorized user ingredient API"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="test123"
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredient list"""

        Ingredient.objects.create(user=self.user, name="Kale")
        Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.get(INGREDIENT_URL)
        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that ingredients for authenticated user only"""

        user2 = get_user_model().objects.create_user(
            email="user2@test.com",
            password="user2123"
        )

        Ingredient.objects.create(user=user2, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Turmeric")

        res = self.client.get(INGREDIENT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)

    def test_create_ingredient(self):
        """Test that creating a new ingredient"""

        payload = {"name": "Cabbage"}
        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(
            user=self.user,
            name=payload["name"]
        ).exists()

        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Test creating invalid ingredient fails"""
        payload = {"name": ""}
        res = self.client.post(INGREDIENT_URL, payload)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)