from django.urls import path

from . import views

urlpatterns = [
    path("active_listings", views.active_listings, name="active_listings"),
    path("", views.home, name="home"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("product/<str:name>", views.product, name="product"),
    path("create_listing", views.create_listing, name="create_listing"),
    path("categories", views.categories, name="categories"),
    path("category/<str:category>", views.category, name="category"),
    path("comment/<str:name>", views.comment, name="comment"),
    path("Watchlist",views.Watchlist, name="Watchlist"),
    path("watchlist/<str:name>", views.watchlist, name="watchlist"),
    path("closedlisting", views.closedlisting, name="closedlisting"),
    path("closebid/<str:name>", views.closebid, name="closebid")
]
