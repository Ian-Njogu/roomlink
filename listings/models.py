from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from cloudinary.models import CloudinaryField
from django.utils import timezone

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = CloudinaryField('profile_pictures', blank=True, null=True)
    is_landlord = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Listing(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('room', 'Room'),
        ('studio', 'Studio'),
        ('shared_room', 'Shared Room'),
    ]
    
    FURNISHED_CHOICES = [
        ('furnished', 'Furnished'),
        ('semi_furnished', 'Semi-Furnished'),
        ('unfurnished', 'Unfurnished'),
    ]
    
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    furnished = models.CharField(max_length=20, choices=FURNISHED_CHOICES)
    location = models.CharField(max_length=200)
    address = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    bedrooms = models.PositiveIntegerField()
    bathrooms = models.PositiveIntegerField()
    square_feet = models.PositiveIntegerField(blank=True, null=True)
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    # Contact information
    contact_phone = models.CharField(max_length=15, blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Amenities (as a text field for now, could be expanded to a separate model)
    amenities = models.TextField(blank=True)
    
    # Image fields
    main_image = CloudinaryField('listing_images', blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('listing_detail', kwargs={'pk': self.pk})

class ListingImage(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('listing_images')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['uploaded_at']
    
    def __str__(self):
        return f"Image for {self.listing.title}"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'listing']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} favorited {self.listing.title}"
