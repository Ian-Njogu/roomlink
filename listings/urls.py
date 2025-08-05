from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('register/', views.register, name='register'),
    path('search/', views.search_listings, name='search'),
    
    # Listing views
    path('listing/create/', views.create_listing, name='create_listing'),
    path('listing/<int:pk>/', views.listing_detail, name='listing_detail'),
    path('listing/<int:pk>/edit/', views.edit_listing, name='edit_listing'),
    path('listing/<int:pk>/delete/', views.delete_listing, name='delete_listing'),
    
    # User profile
    path('profile/', views.profile, name='profile'),
    
    # Favorites
    path('listing/<int:pk>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    
    path('debug-urls/', views.debug_urls, name='debug_urls'),
] 
