from django.contrib import admin
from import_export.admin import ExportActionMixin, ImportExportMixin
from import_export.formats import base_formats
from import_export.resources import ModelResource
from .models import Song


class NeedsInfoFilter(admin.SimpleListFilter):
    title = "needs info"
    parameter_name = "needs"

    def lookups(self, request, model_admin):
        return [("artist", "Missing artist"), ("search_title", "Missing searchable title")]

    def queryset(self, request, queryset):
        if self.value() == "artist":
            return queryset.filter(artist="")
        if self.value() == "search_title":
            return queryset.filter(search_title="")
        return queryset

class SongResource(ModelResource):
    class Meta:
        model = Song
        import_id_fields = ("file_path",)
        fields = ("file_path", "title", "search_title", "artist", "source_media", "aliases")
        export_order = fields
        clean_model_instances = True
        skip_unchanged = True
        report_skipped = True

class ExcelCSV(base_formats.CSV):
    def export_data(self, dataset, **kwargs):
        return "\ufeff" + super().export_data(dataset, **kwargs)

@admin.register(Song)
class SongAdmin(ImportExportMixin, admin.ModelAdmin):
    model = Song
    list_display = ("title", "search_title", "artist", "source_media", "file_found")
    list_display_links = ("title",)
    list_editable = ("artist", "search_title", "source_media")
    list_filter = (NeedsInfoFilter,)
    search_fields = ("title", "search_title", "artist", "source_media", "aliases", "file_path")
    list_per_page = 100
    resource_classes = [SongResource]
    export_formats = [ExcelCSV]
    import_formats = [base_formats.CSV]
    
    @admin.display(boolean=True, description="File found")
    def file_found(self, obj):
        path = obj.absolute_path()
        return None if path is None else path.is_file()
