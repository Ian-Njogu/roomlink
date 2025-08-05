from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from .models import Listing, UserProfile, Favorite, ListingImage
from .forms import UserRegistrationForm, UserProfileForm, ListingForm, ListingImageForm, SearchForm

def home(request):
    """Home page with featured listings and search form"""
    search_form = SearchForm(request.GET)
    listings = Listing.objects.filter(is_active=True, availability='available')
    
    # Apply search filters
    if search_form.is_valid():
        location = search_form.cleaned_data.get('location')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        
        if location:
            listings = listings.filter(location__icontains=location)
        if property_type:
            listings = listings.filter(property_type=property_type)
        if min_price:
            listings = listings.filter(price__gte=min_price)
        if max_price:
            listings = listings.filter(price__lte=max_price)
        if bedrooms:
            listings = listings.filter(bedrooms__gte=bedrooms)
    
    # Pagination
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_listings': listings.count(),
    }
    return render(request, 'listings/home.html', context)

def listing_detail(request, pk):
    """Detail view for a single listing"""
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    is_favorited = False
    
    if request.user.is_authenticated:
        is_favorited = Favorite.objects.filter(user=request.user, listing=listing).exists()
    
    context = {
        'listing': listing,
        'is_favorited': is_favorited,
    }
    return render(request, 'listings/listing_detail.html', context)

def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            login(request, user)
            messages.success(request, 'Account created successfully! Welcome to RoomLink Nairobi!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'listings/register.html', {'form': form})

@login_required
def profile(request):
    """User profile view"""
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)
    
    # Get user's listings and favorites
    user_listings = Listing.objects.filter(posted_by=request.user).order_by('-created_at')
    user_favorites = Favorite.objects.filter(user=request.user).select_related('listing').order_by('-created_at')
    
    context = {
        'form': form,
        'profile': profile,
        'user_listings': user_listings,
        'user_favorites': user_favorites,
    }
    return render(request, 'listings/profile.html', context)

@login_required
@login_required
def create_listing(request):
    """Create a new listing"""
    if request.method == 'POST':
        print("POST request received")  # Debug
        form = ListingForm(request.POST, request.FILES)
        print(f"Form is valid: {form.is_valid()}")  # Debug
        
        if form.is_valid():
            listing = form.save(commit=False)
            listing.posted_by = request.user
            listing.save()
            print(f"Listing saved with pk: {listing.pk}")  # Debug
            
            # Test the reverse before redirecting
            from django.urls import reverse
            try:
                test_url = reverse('listing_detail', kwargs={'pk': listing.pk})
                print(f"Reverse URL works: {test_url}")  # Debug
                messages.success(request, 'Listing created successfully!')
                return redirect('listing_detail', pk=listing.pk)
            except Exception as e:
                print(f"Reverse failed: {e}")  # Debug
                messages.error(request, f'Listing created but redirect failed: {e}')
                return redirect('home')
        else:
            print(f"Form errors: {form.errors}")  # Debug
    else:
        form = ListingForm()
    
    return render(request, 'listings/listing_form.html', {'form': form, 'title': 'Create New Listing'})

@login_required
def edit_listing(request, pk):
    """Edit an existing listing"""
    listing = get_object_or_404(Listing, pk=pk, posted_by=request.user)
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, 'Listing updated successfully!')
            return redirect('listing_detail', pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    
    return render(request, 'listings/listing_form.html', {'form': form, 'title': 'Edit Listing'})

@login_required
def delete_listing(request, pk):
    """Delete a listing"""
    listing = get_object_or_404(Listing, pk=pk, posted_by=request.user)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, 'Listing deleted successfully!')
        return redirect('profile')
    
    return render(request, 'listings/listing_confirm_delete.html', {'listing': listing})

@login_required
@require_POST
def toggle_favorite(request, pk):
    """Toggle favorite status for a listing"""
    listing = get_object_or_404(Listing, pk=pk, is_active=True)
    favorite, created = Favorite.objects.get_or_create(user=request.user, listing=listing)
    
    if not created:
        favorite.delete()
        is_favorited = False
    else:
        is_favorited = True
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorited': is_favorited,
            'message': 'Added to favorites!' if is_favorited else 'Removed from favorites!'
        })
    
    messages.success(request, 'Added to favorites!' if is_favorited else 'Removed from favorites!')
    return redirect('listing_detail', pk=listing.pk)

def search_listings(request):
    """Advanced search view"""
    search_form = SearchForm(request.GET)
    listings = Listing.objects.filter(is_active=True, availability='available')
    
    if search_form.is_valid():
        location = search_form.cleaned_data.get('location')
        property_type = search_form.cleaned_data.get('property_type')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        bedrooms = search_form.cleaned_data.get('bedrooms')
        
        if location:
            listings = listings.filter(location__icontains=location)
        if property_type:
            listings = listings.filter(property_type=property_type)
        if min_price:
            listings = listings.filter(price__gte=min_price)
        if max_price:
            listings = listings.filter(price__lte=max_price)
        if bedrooms:
            listings = listings.filter(bedrooms__gte=bedrooms)
    
    # Pagination
    paginator = Paginator(listings, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_listings': listings.count(),
    }
    return render(request, 'listings/search.html', context)

def about(request):
    """About page"""
    return render(request, 'listings/about.html')

def contact(request):
    """Contact page"""
    return render(request, 'listings/contact.html')
