import datetime as dt

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser

USER, MODERATOR, ADMIN = 'user', 'moderator', 'admin'
ROLES_CHOICES = [
    (USER, 'Пользователь'),
    (MODERATOR, 'Модератор'),
    (ADMIN, 'Админ'),
]


def current_year():
    return dt.date.today().year


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    first_name = models.CharField(
        max_length=150,
        blank=True
    )
    last_name = models.CharField(
        max_length=150,
        blank=True
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    role = models.CharField(
        max_length=16,
        choices=ROLES_CHOICES,
        default=USER
    )

    @property
    def is_admin(self):
        return self.is_staff or self.role == ADMIN

    @property
    def is_moderator(self):
        return self.role == MODERATOR

    @property
    def is_user(self):
        return self.role == USER

    class Meta:
        ordering = ['username']


class Category(models.Model):
    name = models.CharField(
        verbose_name='categories',
        max_length=200
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        verbose_name='genres',
        max_length=200
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(
        verbose_name='title',
        max_length=200,
        null=False,
    )
    year = models.IntegerField(
        verbose_name='yaers',
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(current_year())]
    )
    description = models.TextField(
        verbose_name='description'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        verbose_name='genres'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        db_column='category',
        related_name='categories',
    )

    class Meta:
        verbose_name = 'произведение'
        verbose_name_plural = 'произведения'
        ordering = ['name']

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )

    class Meta:
        db_table = 'reviews_genre_title'

    def __str__(self):
        return f'{self.genre} {self.title}'


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        ordering = ['author']
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique author-title review'
            ),
        )

    def __str__(self):
        mini_title = str(self.title)[:20]
        return f'({self.title.pk}){mini_title} - ({self.pk}){self.text}'[:50]


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        ordering = ['author']
