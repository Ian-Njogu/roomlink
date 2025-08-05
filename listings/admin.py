from django.contrib import admin
from .models import Listing, UserProfile, Favorite, ListingImage

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'is_landlord', 'created_at']
    list_filter = ['is_landlord', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'posted_by', 'location', 'price', 'property_type', 'availability', 'is_active', 'created_at']
    list_filter = ['property_type', 'furnished', 'availability', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'location', 'address', 'posted_by__username']
    list_editable = ['availability', 'is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'posted_by', 'is_active')
        }),
        ('Property Details', {
            'fields': ('property_type', 'furnished', 'bedrooms', 'bathrooms', 'square_feet')
        }),
        ('Location & Pricing', {
            'fields': ('location', 'address', 'price', 'availability')
        }),
        ('Contact Information', {
            'fields': ('contact_phone', 'contact_email')
        }),
        ('Additional Information', {
            'fields': ('amenities', 'main_image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(ListingImage)
class ListingImageAdmin(admin.ModelAdmin):
    list_display = ['listing', 'caption', 'uploaded_at']
    list_filter = ['uploaded_at']
    search_fields = ['listing__title', 'caption']

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'listing__title']
