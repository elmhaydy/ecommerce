from django.db import models

# Create your models here.
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name_fr = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100, blank=True, null=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ["name_fr"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_fr)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_fr


class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name="products"
    )
    name_fr = models.CharField(max_length=150)
    name_en = models.CharField(max_length=150, blank=True, null=True)
    slug = models.SlugField(max_length=170, unique=True, blank=True)

    description_fr = models.TextField()
    description_en = models.TextField(blank=True, null=True)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    image = models.ImageField(upload_to="products/", blank=True, null=True)
    gallery_image_1 = models.ImageField(upload_to="products/gallery/", blank=True, null=True)
    gallery_image_2 = models.ImageField(upload_to="products/gallery/", blank=True, null=True)
    gallery_image_3 = models.ImageField(upload_to="products/gallery/", blank=True, null=True)
    gallery_image_4 = models.ImageField(upload_to="products/gallery/", blank=True, null=True)

    feature_1 = models.CharField(max_length=180, blank=True)
    feature_2 = models.CharField(max_length=180, blank=True)
    feature_3 = models.CharField(max_length=180, blank=True)
    feature_4 = models.CharField(max_length=180, blank=True)
    colors = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_fr)
        super().save(*args, **kwargs)

    def is_in_stock(self):
        return self.stock > 0

    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def get_gallery_images(self):
        return [
            image for image in [
                self.image,
                self.gallery_image_1,
                self.gallery_image_2,
                self.gallery_image_3,
                self.gallery_image_4,
            ] if image
        ]

    def get_feature_list(self):
        return [
            feature for feature in [
                self.feature_1,
                self.feature_2,
                self.feature_3,
                self.feature_4,
            ] if feature
        ]

    def get_color_list(self):
        return [color.strip() for color in self.colors.split(",") if color.strip()]
    
    def __str__(self):
        return self.name_fr
