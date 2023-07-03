from django.contrib import admin
from .models import Flight, AirwaysPilot, Airways, Ballon, Pilot


class AirwaysPilotAdmin(admin.TabularInline):
    model = AirwaysPilot
    extra = 0


class AirwaysAdmin(admin.ModelAdmin):
    inlines = [AirwaysPilotAdmin, ]
    list_display = ("name",)


admin.site.register(Airways, AirwaysAdmin)


class FlightAdmin(admin.ModelAdmin):
    exclude = ('user',)

    def save_model(self, request, obj, form, change):
        obj.user = request.user
        return super().save_model(request, obj, form,
                                  change)

    def has_change_permission(self, request, obj=None):
        if obj and obj.user == request.user:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Flight, FlightAdmin)
admin.site.register(Ballon)


class PilotAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name")


admin.site.register(Pilot, PilotAdmin)
