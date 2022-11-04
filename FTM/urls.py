from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

router = DefaultRouter()
user = router.register("user",views.UserView)
router.register("profile", views.ProfileView)
router.register("workExp", views.WorkExpView)
router.register("reviews", views.ReviewsView)
router.register('friends', views.FriendViewSet, 'friend')

urlpatterns = [
    path('api/', include(router.urls), name = 'create-profile'),
    path('register/', views.RegisterUserAPIView.as_view(), name = "register"),
    path('get-profile/', views.GetProfile.as_view(), name = 'get-profile'),
    path('api-auth/', include('rest_framework.urls')),
    path('login/', views.LoginView.as_view(), name='login'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
