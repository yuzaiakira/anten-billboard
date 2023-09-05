from django.contrib import admin
from billboard import models
from adminpanel.models import UserModel


# Register inlines admin class
class BillboardFinalPriceInline(admin.TabularInline):
    model = models.BillboardFinalPriceModel
    readonly_fields = ('final_price',)


class BillboardImageInline(admin.TabularInline):
    model = models.BillboardImageModel
    extra = 2


# Register models admin class
@admin.register(models.BillboardModel)
class BillboardAdmin(admin.ModelAdmin):
    commission = 1.2
    list_display = ('name', 'reseller', 'city', 'reservation_date', 'get_final_price')
    list_filter = ('reseller', 'city', 'reservation_date', 'attribute', 'billboard_length',
                   'billboard_width', 'has_power')
    search_fields = ('name', 'reseller', 'city', 'address')
    prepopulated_fields = {'url': ('title',), }
    filter_horizontal = ('attribute',)
    inlines = (BillboardImageInline, )
    fieldsets = (("توضیحات بیلبورد",
                  {
                      "fields": ("city", "name", "address", "attribute", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power", ("billboard_length", "billboard_width", "price", "reservation_date")),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "url", "desc"),
                  }),

                 )

    def get_final_price(self, obj):
        return obj.BillboardFinalPriceModel.final_price

    get_final_price.short_description = 'قیمت'

    def save_model(self, request, obj, form, change):
        if getattr(obj, 'reseller') is None:
            obj.reseller = request.user

        super().save_model(request, obj, form, change)

    def response_add(self, request, obj, post_url_continue=None):
        final_price_model, created = models.BillboardFinalPriceModel.objects.get_or_create(billboard=obj)
        if obj.reseller.user_group == UserModel.ADMIN_USER:
            final_price = obj.price
        else:
            final_price = (obj.price * self.commission) + obj.BillboardFinalPriceModel.add_price

        if created:
            final_price_model.final_price = final_price
            final_price_model.add_price = obj.BillboardFinalPriceModel.add_price

        else:
            final_price_model.final_price = final_price

        final_price_model.save()

        return super(BillboardAdmin, self).response_add(request, obj, post_url_continue)

    def response_change(self, request, obj):
        final_price_model = models.BillboardFinalPriceModel.objects.get(billboard=obj)
        if obj.reseller.user_group != UserModel.ADMIN_USER:
            final_price = (obj.price * self.commission) + obj.BillboardFinalPriceModel.add_price
            if final_price != obj.BillboardFinalPriceModel.final_price:
                final_price_model.final_price = final_price
        else:
            final_price_model.final_price = obj.price

        final_price_model.add_price = obj.BillboardFinalPriceModel.add_price
        final_price_model.save()

        return super(BillboardAdmin, self).response_change(request, obj)

    def get_fieldsets(self, request, obj=None):
        if self.fieldsets:
            if request.user.user_group == UserModel.ADMIN_USER:
                fieldsets = (("توضیحات بیلبورد", {
                      "fields": ("city", "name", "address", "attribute", "description",),
                  }),
                 ("ویژگی های بیلورد",
                  {
                      "fields": ("has_power", "reseller", ("billboard_length", "billboard_width",
                                                           "price", "reservation_date")),
                  }),
                 ("سئو",
                  {
                      "fields": ("billboard_pic", "map_iframe", "title", "url", "desc"),
                  }),

                 )
                return fieldsets
            else:
                return self.fieldsets
        return [(None, {'fields': self.get_fields(request, obj)})]

    def get_inlines(self, request, obj):
        if request.user.user_group == UserModel.ADMIN_USER:
            try:
                if obj.reseller.user_group == UserModel.ADMIN_USER:
                    new_inlines = (BillboardImageInline, )

            except AttributeError:
                new_inlines = (BillboardFinalPriceInline, BillboardImageInline)

            return new_inlines

        else:
            return super().get_inlines(request, obj)

    def get_queryset(self, request):
        qs = self.model.object.by_reseller(request)
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs


@admin.register(models.StateModel)
class StateAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


@admin.register(models.CityModel)
class CityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'url': ('title',), }


# Register models
admin.site.register(models.BillboardImageModel)
admin.site.register(models.BillboardFinalPriceModel)
admin.site.register(models.BillboardAttributeModel)
