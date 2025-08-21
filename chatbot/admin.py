from django.contrib import admin
from .models import Node, Option

class OptionInline(admin.TabularInline):
    model = Option
    fk_name = "from_node"   # tell Django which ForeignKey links to Node
    extra = 1


class NodeAdmin(admin.ModelAdmin):
    list_display = ("name", "message")
    inlines = [OptionInline]

admin.site.register(Node, NodeAdmin)