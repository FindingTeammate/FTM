from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework import urls
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
user = router.register("user",views.UserView)
router.register("profile", views.ProfileView)
router.register("workExp", views.WorkExpView)
router.register("reviews", views.ReviewsView)

urlpatterns = [
    path('api/', include(router.urls), name = 'create-profile'),
    path('register/', views.RegisterUserAPIView.as_view(), name = "register"),
    path('get-profile/', views.GetProfile.as_view(), name = 'get-profile'),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
