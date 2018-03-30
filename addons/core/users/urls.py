from django.urls import path
from .views import Users, UserDetail

urlpatterns = (
    path('', Users.as_view(), name='users'),
    path('<int:pk>/', UserDetail.as_view(), name='user-detail')
)
