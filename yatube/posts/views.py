from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related('author', 'group'),
                settings.POSTS_ON_PAGE,
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    return render(
        request,
        'posts/group_list.html',
        {
            'group': get_object_or_404(Group, slug=slug),
            'page_obj': paginate(
                request,
                get_object_or_404(Group, slug=slug).posts.select_related(
                    'author',
                    'group',
                ),
                settings.POSTS_ON_PAGE,
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    return render(
        request,
        'posts/profile.html',
        {
            'author': get_object_or_404(User, username=username),
            'page_obj': paginate(
                request,
                get_object_or_404(
                    User,
                    username=username,
                ).posts.select_related('author', 'group'),
                settings.POSTS_ON_PAGE,
            ),
            'following': (
                request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user,
                    author=get_object_or_404(User, username=username),
                ).exists()
            ),
        },
    )


def post_detail(request: HttpRequest, id: int) -> HttpResponse:
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': get_object_or_404(Post, pk=id),
            'form': CommentForm(),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request: HttpRequest, id: int) -> HttpResponse:
    if get_object_or_404(Post, pk=id).author != request.user:
        return redirect('posts:post_detail', get_object_or_404(Post, pk=id).pk)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=get_object_or_404(Post, id=id),
    )
    if form.is_valid():
        form.instance.author = request.user
        form.save()
        return redirect(
            'posts:post_detail',
            id=get_object_or_404(Post, pk=id).pk,
        )
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
            'post': get_object_or_404(Post, pk=id),
        },
    )


@login_required
def add_comment(request: HttpRequest, id: int) -> HttpResponse:
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = get_object_or_404(Post, id=id)
        form.save()
    return redirect('posts:post_detail', id=id)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.filter(author__following__user=request.user),
                settings.POSTS_ON_PAGE,
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    if get_object_or_404(User, username=username) != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=get_object_or_404(User, username=username),
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str):
    get_object_or_404(
        request.user.follower,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username=username)
