from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.vary import vary_on_cookie
from django.views.decorators.cache import cache_page
from .models import Post, Group, Follow, User
from .forms import PostForm, CommentForm
from .utils import get_paginator
from yatube.settings import POSTS_PER_PAGE


@cache_page(20, key_prefix='index_page')
@vary_on_cookie
def index(request):
    posts = Post.objects.all()
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    context = {
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


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
    posts = Post.objects.filter(author=author).all()
    user = request.user
    page_obj = get_paginator(request, posts, POSTS_PER_PAGE)
    follow = Follow.objects.filter(
        author=author,
        user=user
    )
    following = False
    if follow.exists() and author != user:
        following = True
    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)

@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_obj = Follow.objects.filter(
        author=author,
        user=user
    )
    if not follow_obj.exists() and author != user:
        Follow.objects.create(
            author=author,
            user=user
        )
        return redirect('posts:profile', username=author)
    return redirect('posts:profile', username=author)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(
            request,
            'posts/create_post.html',
            {'form': form}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow = Follow.objects.filter(
        author=author,
        user=user
    )
    if not follow.exists() and author != user:
        Follow.objects.create(
            user=user,
            author=author,
        )
        return redirect('posts:profile', username=author)
    return redirect('posts:profile', username=author)

@login_required
def profile_unfollow(request, username):
    user = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=user).delete()
    return redirect('posts:profile', username=username)