from rest_framework import serializers

from reviews.models import User, Title, Genre, Category, Review, Comment


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя me запрещено!'
            )
        return value


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField(
        max_length=254,
        required=True,

    )
    username = serializers.CharField(
        required=True
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя me запрещено!'
            )
        elif User.objects.filter(username__iexact=value.lower()):
            raise serializers.ValidationError('Пользователь уже существует')
        return value

    def validate_email(self, value):
        lower_email = value.lower()
        if User.objects.filter(email__iexact=value.lower()).exists():
            raise serializers.ValidationError('Пользователь с данным email '
                                              'уже существует.')
        return lower_email


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(
        required=True
    )
    confirmation_code = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        exclude = ('id',)


class TitleSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(required=False)

    class Meta:
        fields = '__all__'
        model = Title


class CreateTitleSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug', many=True
    )

    class Meta:
        fields = '__all__'
        model = Title


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
        read_only_fields = ('id', 'author', 'pub_date', 'review')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('id', 'author', 'pub_date')

    def validate(self, data):
        if self.context['request'].method == 'POST':
            title_id = (
                self.context['request'].parser_context['kwargs']['title_id']
            )
            user = self.context['request'].user
            if user.reviews.filter(title_id=title_id).exists():
                raise serializers.ValidationError(
                    'Второй отзыв от автора на одно произведение.'
                )
        return data
