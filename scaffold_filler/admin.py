from django.contrib import admin
from .models import PredictionHistory


@admin.register(PredictionHistory)
class PredictionHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'gap_count', 'avg_confidence', 'created_at')
    list_filter = ('created_at',)
    readonly_fields = ('input_scaffold', 'output_filled', 'gap_count',
                       'avg_confidence', 'created_at')
