from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from .models import *
from accounts.models import User

SUBSCRIPTION_STATUS = (
    ('Subscribed', 'Subscribed'),
    ('Unsubscribed', 'Unsubscribed'),
    ('Trial', 'Trial'),
    ('Expired', 'Expired'),
)

SUBSCRIPTION_PERIOD = (
    ('Trial', 'Trial'),
    ('Monthly', 'Monthly'),
    ('Yearly', 'Yearly'),
)


class SubscriptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    subscription_id = serializers.CharField(required=True)
    status = serializers.ChoiceField(choices=SUBSCRIPTION_STATUS, required=True)
    period = serializers.ChoiceField(choices=SUBSCRIPTION_PERIOD, required=True)
    start_date = serializers.DateTimeField(required=True)
    cancel_date = serializers.DateTimeField(required=False)
    end_date = serializers.DateTimeField(required=False)

    class Meta:
        model = Subscription
        fields = ('id', 'user', 'subscription_id', 'status', 'period', 'start_date', 'cancel_date', 'end_date')

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['request'].user
            subscription_id = validated_data.get('subscription_id')
            status = validated_data.get('status')
            period = validated_data.get('period')
            start_date = validated_data.get('start_date')

            if period == 'Trial':
                end_date = start_date + relativedelta(days=7)
            elif period == 'Monthly':
                end_date = start_date + relativedelta(months=1)
            elif period == 'Yearly':
                end_date = start_date + relativedelta(years=1)

            subscription = Subscription.objects.create(
                user=user,
                subscription_id=subscription_id,
                status=status,
                period=period,
                start_date=start_date,
                end_date=end_date,
            )
            return subscription
