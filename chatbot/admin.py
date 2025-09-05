from django.contrib import admin
from .models import Node, Option, UserInquiry
import csv
from django.http import HttpResponse

# Your existing admin registrations
class OptionInline(admin.TabularInline):
    model = Option
    fk_name = "from_node"
    extra = 1

class NodeAdmin(admin.ModelAdmin):
    list_display = ("name", "message")
    inlines = [OptionInline]

class UserInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "service", "created_at", "email_confirmed")
    list_filter = ("service", "created_at", "email_confirmed")
    search_fields = ("name", "email", "service")
    
    # Add CSV export action
    actions = ['export_as_csv']
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
            
        return response
        
    export_as_csv.short_description = "Export Selected as CSV"

admin.site.register(Node, NodeAdmin)
admin.site.register(UserInquiry, UserInquiryAdmin)  # Register the new model