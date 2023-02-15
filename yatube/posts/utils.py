from django.core.paginator import Paginator


def get_paginator(request, posts, POSTS_PER_PAGE):
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
