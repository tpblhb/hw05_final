from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.select_related('author', 'group')
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(request, posts, settings.POSTS_ON_PAGE),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author', 'group')
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(request, posts, settings.POSTS_ON_PAGE),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author', 'group')
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(request, posts, settings.POSTS_ON_PAGE),
            'following': following,
        },
    )


def post_detail(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=id)
    form = CommentForm()
    comments = post.comments.all()
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': form,
            'comments': comments,
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:profile', request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=id)
    if post.author != request.user:
        return redirect('posts:post_detail', post.pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect('posts:post_detail', id=post.pk)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
            'post': post,
        },
    )


@login_required
def add_comment(request: HttpRequest, id: int) -> HttpResponse:
    post = get_object_or_404(Post, id=id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', id=id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(request, posts, settings.POSTS_ON_PAGE),
        },
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect("posts:profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect("posts:profile", username=username)
