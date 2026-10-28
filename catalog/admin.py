from django.contrib import admin
from catalog.models import PetCategory, PetBreed, Pet, PetImage, HealthDocument

class PetImageInline(admin.TabularInline):
    model = PetImage
    extra = 1

class HealthDocumentInline(admin.StackedInline):
    model = HealthDocument
    extra = 1

@admin.register(PetCategory)
class PetCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active', 'display_order', 'created_at')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('is_active',)

@admin.register(PetBreed)
class PetBreedAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'slug', 'hypoallergenic', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'hypoallergenic', 'is_active')

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'reference_number', 'breed', 'category', 'price', 'status', 'sex', 'is_published', 'is_featured')
    list_filter = ('status', 'is_published', 'is_featured', 'category', 'breed', 'sex')
    search_fields = ('name', 'reference_number', 'microchip_id', 'description')
    prepopulated_fields = {'slug': ('name', 'reference_number')}
    inlines = [PetImageInline, HealthDocumentInline]

@admin.register(PetImage)
class PetImageAdmin(admin.ModelAdmin):
    list_display = ('pet', 'is_primary', 'display_order', 'caption')

@admin.register(HealthDocument)
class HealthDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'pet', 'document_type', 'issuing_veterinarian', 'issued_date')
    list_filter = ('document_type', 'issued_date')
