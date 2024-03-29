from django.contrib.auth import views
from django.urls import include, path, reverse_lazy

from users.apps import UsersConfig
from users.views import SignUp

app_name = UsersConfig.name

passwords = [
    path(
        'reset/',
        views.PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'change/',
        views.PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done'),
        ),
        name='password_change',
    ),
    path(
        'change/done/',
        views.PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html',
        ),
        name='password_change_done',
    ),
    path(
        'reset/done/',
        views.PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64/<token>/',
        views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
        ),
    ),
    path(
        'reset/done/',
        views.PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html',
        ),
    ),
]

urlpatterns = [
    path('signup/', SignUp.as_view(), name='signup'),
    path(
        'logout/',
        views.LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout',
    ),
    path(
        'login/',
        views.LoginView.as_view(template_name='users/login.html'),
        name='login',
    ),
    path(
        'passwords/',
        include(passwords),
    ),
]
