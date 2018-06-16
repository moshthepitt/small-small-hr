"""
Serializers for users app
"""
from django.contrib.auth.models import User

from rest_framework import serializers

from small_small_hr.models import StaffProfile


# pylint: disable=too-many-ancestors
class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer class
    """

    class Meta(object):  # pylint:  disable=too-few-public-methods
        """
        meta options
        """
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')


class StaffProfileSerializer(serializers.ModelSerializer):
    """
    Serializer class for StaffProfile model
    """
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    id_number = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    sex = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    nhif = serializers.SerializerMethodField()
    nssf = serializers.SerializerMethodField()
    pin_number = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    birthday = serializers.SerializerMethodField()
    leave_days = serializers.SerializerMethodField()
    sick_days = serializers.SerializerMethodField()
    overtime_allowed = serializers.SerializerMethodField()
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    emergency_contact_name = serializers.SerializerMethodField()
    emergency_contact_number = serializers.SerializerMethodField()

    class Meta(object):  # pylint:  disable=too-few-public-methods
        """
        class meta options
        """
        model = StaffProfile
        fields = [
            'id',
            'created',
            'modified',
            'first_name',
            'last_name',
            'id_number',
            'phone',
            'sex',
            'role',
            'nhif',
            'nssf',
            'pin_number',
            'address',
            'birthday',
            'leave_days',
            'sick_days',
            'overtime_allowed',
            'start_date',
            'end_date',
            'emergency_contact_name',
            'emergency_contact_number',
        ]

    def get_id_number(self, obj):
        """
        Get id_number
        """
        return obj.data.get('id_number')

    def get_phone(self, obj):
        """
        Get phone
        """
        return obj.data.get('phone')

    def get_sex(self, obj):
        """
        Get sex
        """
        return obj.data.get('sex')

    def get_role(self, obj):
        """
        Get role
        """
        return obj.data.get('role')

    def get_nhif(self, obj):
        """
        Get nhhf
        """
        return obj.data.get('nhif')

    def get_nssf(self, obj):
        """
        Get nssf
        """
        return obj.data.get('nssf')

    def get_pin_number(self, obj):
        """
        Get pin_number
        """
        return obj.data.get('pin_number')

    def get_address(self, obj):
        """
        Get address
        """
        return obj.data.get('address')

    def get_birthday(self, obj):
        """
        Get birthday
        """
        return obj.data.get('birthday')

    def get_leave_days(self, obj):
        """
        Get leave_days
        """
        return obj.data.get('leave_days')

    def get_sick_days(self, obj):
        """
        Get sick_days
        """
        return obj.data.get('sick_days')

    def get_overtime_allowed(self, obj):
        """
        Get overtime_allowed
        """
        return obj.data.get('overtime_allowed')

    def get_start_date(self, obj):
        """
        Get start_date
        """
        return obj.data.get('start_date')

    def get_end_date(self, obj):
        """
        Get end_date
        """
        return obj.data.get('end_date')

    def get_emergency_contact_name(self, obj):
        """
        Get emergency_contact_name
        """
        return obj.data.get('emergency_contact_name')

    def get_emergency_contact_number(self, obj):
        """
        Get emergency_contact_number
        """
        return obj.data.get('emergency_contact_number')
