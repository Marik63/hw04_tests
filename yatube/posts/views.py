from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from .models import (Group, Post, User)
from .forms import PostForm
from .utils import page


def index(request):
    post_list = Post.objects.select_related('author', 'group')
    page_obj = page(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Возращает 10 постов указанной темы"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')
    page_obj = page(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Показывает профиль пользователя"""
    author = get_object_or_404(User, username=username)
    posts_count = author.posts.count()
    post_list = author.posts.select_related('author', 'group')
    page_object = page(request, post_list)
    context = {
        'author': author,
        'page_obj': page_object,
        'posts_amount': posts_count,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Показывает пост"""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Создаёт новый пост"""
    form = PostForm(
        request.POST or None
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    temp_form = form.save(commit=False)
    temp_form.author = request.user
    temp_form.save()
    return redirect(
        'posts:profile', temp_form.author
    )


@login_required
def post_edit(request, post_id):
    """Редактирует пост"""
    post = get_object_or_404(Post, id=post_id)
    is_edit = True
    if request.user != post.author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post': post,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)
