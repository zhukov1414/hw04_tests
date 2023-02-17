"""
Файл тестирования html-страничек
"""

from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    """
    Класс тестирования html-страниц
    """
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username="StasBasov")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Тестовое описание",
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text="Тестовый пост",
            group=cls.group,
        )

        # Списки точек сайта
        cls.templates_pages_names = {
            "posts:index": "posts/index.html",
            "posts:group_list": "posts/group_list.html",
            "posts:profile": "posts/profile.html",
            "posts:post_detail": "posts/post_detail.html",
            "posts:post_edit": "posts/create_post.html",
            "posts:post_create": "posts/create_post.html",
        }

        # Аргументы точек сайта
        cls.templates_pages_args = {
            "posts:index": {},
            "posts:group_list": {'slug': cls.group.slug},
            "posts:profile": {"username": cls.post.author},
            "posts:post_detail": {"post_id": cls.post.id},
            "posts:post_edit": {"post_id": cls.post.id},
            "posts:post_create": {},
        }
        cls.reverse_names = {reverse_name: reverse(reverse_name,
                                                   kwargs=cls.templates_pages_args[reverse_name])
                             for reverse_name in cls.templates_pages_names}

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template_name in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(self.reverse_names[reverse_name])
                self.assertTemplateUsed(response, template_name)

    def test_index_show_correct_context(self):
        """Список постов в шаблоне index равен ожидаемому контексту."""

        # Тестирование гостя
        response = self.guest_client.get(self.reverse_names["posts:index"])
        first_object = response.context['page_obj'][0]
        obj_data = {
            first_object.text: 'Тестовый пост',
            first_object.author: self.user,
            first_object.group: self.group,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

        # Тестирование аворизованного пользователя
        response = self.authorized_client.get(self.reverse_names['posts:group_list'])
        first_obj = response.context['page_obj'][0]
        obj_data = {
            first_obj.text: 'Тестовый пост',
            first_obj.group: self.group,
            response.context['group']: self.group,
        }
        for obj, data in obj_data.items():
            with self.subTest(obj=obj):
                self.assertEqual(obj, data)

    def test_create_edit_show_correct_context(self):
        """Шаблон create_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(self.reverse_names["posts:post_edit"])
        form_fields = {
            "text": forms.fields.CharField,
            "group": forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)

        response = self.authorized_client.get(self.reverse_names["posts:post_create"])
        form_fields = {
            "text": forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context["form"].fields[value]
                self.assertIsInstance(form_field, expected)
