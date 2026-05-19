from django.db import models
from django.db.models import Q, UniqueConstraint, CheckConstraint
from django.core.validators import MinValueValidator, MaxValueValidator

# class Author(models.Model):
#     name = models.CharField(max_length=100)
#
#
# class Book(models.Model):
#     title = models.CharField(max_length=200)
#     author = models.ForeignKey(Author, on_delete=models.CASCADE)


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Назва категорії")
    slug = models.SlugField(max_length=120, unique=True,
                            help_text="URL-friendly назва")
    description = models.TextField(blank=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"
        ordering = ['name']

        constraints = [
            UniqueConstraint(fields=['name'], name='unique_category_name'),
        ]

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Назва виробника")
    country = models.CharField(max_length=100, verbose_name="Країна")
    website = models.URLField(max_length=200, blank=True, null=True, verbose_name="Веб-сайт")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    logo = models.ImageField(upload_to='manufacturers/logos/', blank=True, null=True, verbose_name="Логотип")
    established_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1800), MaxValueValidator(2026)],
        blank=True, null=True,
        verbose_name="Рік заснування"
    )

    class Meta:
        verbose_name = "Виробник"
        verbose_name_plural = "Виробники"
        ordering = ['name']

        constraints = [
            models.UniqueConstraint(fields=['name'], name='unique_manufacturer_name')
        ]

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опубліковано'),
        ('archived', 'Архівовано'),
    ]

    name = models.CharField(max_length=200, verbose_name="Назва товару")
    slug = models.SlugField(max_length=250, unique=True, verbose_name="Slug")
    description = models.TextField(verbose_name="Опис")
    short_description = models.CharField(max_length=300, blank=True, verbose_name="Короткий опис")

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name="Категорія"
    )

    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name="Виробник"
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Ціна"
    )
    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Ціна зі знижкою"
    )
    stock_quantity = models.PositiveIntegerField(default=0, verbose_name="Кількість на складі")

    sku = models.CharField(max_length=50, unique=True, verbose_name="Артикул (SKU)")
    weight = models.FloatField(null=True, blank=True, verbose_name="Вага (кг)")
    is_available = models.BooleanField(default=True, verbose_name="Доступний для продажу")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name="Статус"
    )
    tags = models.JSONField(default=list, blank=True, verbose_name="Теги")  # сучасний спосіб зберігання списку

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    published_at = models.DateField(null=True, blank=True, verbose_name="Дата публікації")

    additional_categories = models.ManyToManyField(
        Category,
        related_name='additional_products',
        blank=True,
        verbose_name="Додаткові категорії"
    )

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товари"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['price']),
            models.Index(fields=['status']),
        ]

        constraints = [
            UniqueConstraint(fields=['name'], name='unique_product_name'),

            CheckConstraint(condition=Q(price__gte=0), name='check_product_price_positive'),

            CheckConstraint(condition=Q(stock_quantity__gte=0), name='check_stock_quantity_positive'),
        ]

    def __str__(self):
        return self.name

    def get_final_price(self):
        return self.discount_price if self.discount_price else self.price