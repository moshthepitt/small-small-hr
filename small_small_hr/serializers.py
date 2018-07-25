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

    class Meta:  # pylint:  disable=too-few-public-methods
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

    class Meta:  # pylint:  disable=too-few-public-methods
        """
        class meta options
        """
        model = StaffProfile
        fields = [
            'id',
            'first_name',
            'last_name',
            'created',
            'id_number',
            'phone',
            'sex',
            'modified',
            'role',
            'nhif',
            'emergency_contact_name',
            'nssf',
            'address',
            'birthday',
            'overtime_allowed',
            'leave_days',
            'start_date',
            'sick_days',
            'pin_number',
            'end_date',
            'emergency_contact_number',
        ]

    def get_id_number(self, obj):  # pylint: disable=no-self-use
        """
        Get id_number
        """
        return obj.data.get('id_number')

    def get_phone(self, obj):  # pylint: disable=no-self-use
        """
        Get phone
        """
        return obj.data.get('phone')

    def get_sex(self, obj):  # pylint: disable=no-self-use
        """
        Get sex
        """
        return obj.data.get('sex')

    def get_role(self, obj):  # pylint: disable=no-self-use
        """
        Get role
        """
        return obj.data.get('role')

    def get_nhif(self, obj):  # pylint: disable=no-self-use
        """
        Get nhhf
        """
        return obj.data.get('nhif')

    def get_nssf(self, obj):  # pylint: disable=no-self-use
        """
        Get nssf
        """
        return obj.data.get('nssf')

    def get_pin_number(self, obj):  # pylint: disable=no-self-use
        """
        Get pin_number
        """
        return obj.data.get('pin_number')

    def get_address(self, obj):  # pylint: disable=no-self-use
        """
        Get address
        """
        return obj.data.get('address')

    def get_birthday(self, obj):  # pylint: disable=no-self-use
        """
        Get birthday
        """
        return obj.data.get('birthday')

    def get_leave_days(self, obj):  # pylint: disable=no-self-use
        """
        Get leave_days
        """
        return obj.data.get('leave_days')

    def get_sick_days(self, obj):  # pylint: disable=no-self-use
        """
        Get sick_days
        """
        return obj.data.get('sick_days')

    def get_overtime_allowed(self, obj):  # pylint: disable=no-self-use
        """
        Get overtime_allowed
        """
        return obj.data.get('overtime_allowed')

    def get_start_date(self, obj):  # pylint: disable=no-self-use
        """
        Get start_date
        """
        return obj.data.get('start_date')

    def get_end_date(self, obj):  # pylint: disable=no-self-use
        """
        Get end_date
        """
        return obj.data.get('end_date')

    def get_emergency_contact_name(self, obj):  # pylint: disable=no-self-use
        """
        Get emergency_contact_name
        """
        return obj.data.get('emergency_contact_name')

    def get_emergency_contact_number(self, obj):  # pylint: disable=no-self-use
        """
        Get emergency_contact_number
        """
        return obj.data.get('emergency_contact_number')
