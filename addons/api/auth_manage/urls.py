from django.urls import path
from .views import Register, Login, Logout, EditCurrentUser, DeleteCurrentUser, CurrentUser, UserList

app_name = 'register'
urlpatterns = (
    path('register/', Register.as_view(), name='register'),
    path('current-user/', CurrentUser.as_view(), name='get-current-user'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('edit-current-user/', EditCurrentUser.as_view(), name='edit-current-user'),
    path('delete-current-user/', DeleteCurrentUser.as_view(), name='delete-current-user'),
    path('user-list/', UserList.as_view(), name='user-list')
)

