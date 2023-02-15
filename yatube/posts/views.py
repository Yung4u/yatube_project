from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, User
from .forms import PostForm
from .utils import get_paginator
from yatube.settings import POSTS_PER_PAGE


def index(request):
    posts = Post.objects.all()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).all()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            'posts/includes/create_post.html',
            {'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    context = {
        'form': form,
        'post': post,
        'is_edit': True,
    }
    if post.author == request.user:
        if form.is_valid():
            post.save()
            return redirect('posts:post_detail', post_id)
    return render(request, 'posts/includes/create_post.html', context)
