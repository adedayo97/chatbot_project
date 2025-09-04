from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Node, Option, UserProfile
import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str

# Create an inline admin descriptor for UserProfile
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

# Export as CSV action
def export_users_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'
    
    writer = csv.writer(response, csv.excel)
    response.write(u'\ufeff'.encode('utf8'))  # BOM (optional...Excel needs it to open UTF-8 file properly)
    
    # Write headers
    writer.writerow([
        smart_str('Username'),
        smart_str('Email'),
        smart_str('First Name'),
        smart_str('Last Name'),
        smart_str('Phone'),
        smart_str('Country'),
        smart_str('Email Verified'),
        smart_str('Date Joined'),
        smart_str('Last Login'),
        smart_str('Is Active'),
        smart_str('Is Staff'),
        smart_str('Is Superuser'),
    ])
    
    # Write data rows
    for obj in queryset:
        writer.writerow([
            smart_str(obj.username),
            smart_str(obj.email),
            smart_str(obj.first_name),
            smart_str(obj.last_name),
            smart_str(obj.userprofile.phone),
            smart_str(obj.userprofile.country),
            smart_str('Yes' if obj.userprofile.email_verified else 'No'),
            smart_str(obj.date_joined.strftime('%Y-%m-%d %H:%M') if obj.date_joined else ''),
            smart_str(obj.last_login.strftime('%Y-%m-%d %H:%M') if obj.last_login else ''),
            smart_str('Yes' if obj.is_active else 'No'),
            smart_str('Yes' if obj.is_staff else 'No'),
            smart_str('Yes' if obj.is_superuser else 'No'),
        ])
    
    return response
export_users_csv.short_description = "Export selected users to CSV"

# Define a new User admin
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name',  'get_phone', 'get_country', 'get_email_verified', 'date_joined')
    list_filter = ('userprofile__email_verified', 'userprofile__country', 'date_joined', 'is_active')
    actions = [export_users_csv]
    
    def get_phone(self, instance):
        return instance.userprofile.phone
    get_phone.short_description = 'Phone'
    
    def get_country(self, instance):
        return instance.userprofile.country
    get_country.short_description = 'Country'
    
    def get_email_verified(self, instance):
        return instance.userprofile.email_verified
    get_email_verified.short_description = 'Email Verified'
    get_email_verified.boolean = True

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Your existing admin registrations
class OptionInline(admin.TabularInline):
    model = Option
    fk_name = "from_node"
    extra = 1

class NodeAdmin(admin.ModelAdmin):
    list_display = ("name", "message")
    inlines = [OptionInline]

admin.site.register(Node, NodeAdmin)