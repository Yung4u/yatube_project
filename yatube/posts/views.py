from django.shortcuts import render


def index(request):
    template = 'posts/index.html'
    context = {
        'title': 'Социальная сеть для блогеров',
        'text': 'Это главная страница проекта Yatube',
    }
    return render(request, template, context)


def group_posts(request):
    template = 'posts/group_posts.html'
    context = {
        'title': 'Социальная сеть для блогеров',
        'text': 'Здесь будет информация о группах проекта Yatube',
    }
    return render(request, template, context)
