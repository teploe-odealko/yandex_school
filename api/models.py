from django.db import models
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

OFFER = "OFFER"
CATEGORY = "CATEGORY"

MONTH_CHOICES = (
    (OFFER, "OFFER"),
    (CATEGORY, "CATEGORY"),
)


class ShopUnit(models.Model):
    id = models.CharField(primary_key=True, null=False, blank=False, unique=True, max_length=36)
    name = models.TextField(null=False, blank=False)
    date = models.DateTimeField(null=False, blank=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, related_name='children')
    type = models.CharField(choices=MONTH_CHOICES, max_length=8, null=False, blank=False)
    price = models.IntegerField(null=True, blank=False)
    weight = models.IntegerField(null=False, default=0)


class ShopUnitStat(models.Model):
    class Meta:
        unique_together = ('shop_unit_id', 'date',)
    shop_unit_id = models.ForeignKey(ShopUnit, on_delete=models.CASCADE)
    date = models.DateTimeField(null=False, blank=False)
    price = models.IntegerField(null=False, blank=False)
    name = models.TextField(null=False, blank=False)
    parent = models.UUIDField(null=True, blank=False)


@receiver(post_save, sender=ShopUnit, dispatch_uid="update_parent_price")
def update_parent_price(sender, instance, **kwargs):
    parent = instance.parent
    final_price = 0
    if instance.price:
        defaults_instance = dict(
            shop_unit_id=instance,
            price=instance.price,
            date=instance.date,
            name=instance.name,
            parent=instance.parent.id if instance.parent else None,
        )
        ShopUnitStat.objects.update_or_create(
            shop_unit_id=instance,
            date=instance.date,
            defaults=defaults_instance
        )

    if parent:
        parent.weight = parent.children.all().aggregate(Sum('weight'))['weight__sum']
        if not parent.weight:
            return

        for child in parent.children.all():
            if not child.price:
                continue
            final_price += child.price * child.weight
        parent.price = final_price / parent.weight
        parent.date = instance.date
        defaults = dict(
            shop_unit_id=parent,
            price=parent.price,
            date=parent.date,
            name=parent.name,
            parent=parent.parent.id if parent.parent else None,
        )
        ShopUnitStat.objects.update_or_create(
            shop_unit_id=parent, date=parent.date, defaults=defaults
        )
        parent.save()
