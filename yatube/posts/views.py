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
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                group.posts.select_related(
                    'author',
                    'group',
                ),
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(
                request,
                author.posts.select_related('author', 'group'),
            ),
            'following': (
                request.user.is_authenticated
                and Follow.objects.filter(
                    user=request.user,
                    author=author,
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
        return redirect(
            'posts:post_detail',
            id=post.pk,
        )
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
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    get_object_or_404(
        request.user.follower,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username=username)
