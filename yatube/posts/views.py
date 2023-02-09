from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def get_page_context(post_list, request):
    paginator = Paginator(post_list, settings.NUMBER_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    post_list = Post.objects.all().select_related('author', 'group')
    return render(request, 'posts/index.html', {
        'page_obj': get_page_context(post_list, request),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_page_context(post_list, request),
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    return render(request, 'posts/profile.html', {
        'page_obj': get_page_context(post_list, request),
        'author': author,
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {
        'post': post,
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.pk,)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post.pk,)
    return render(request, 'posts/create_post.html', {
        'form': form,
        'is_edit': True})
