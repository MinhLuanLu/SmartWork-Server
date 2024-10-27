from rest_framework import serializers
from .models import User,CheckIn,Employee,Assignment, Order,Conversation
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "FullName", "Email", "Address", "City", "Postcode", "Password","Role", "Policy_agreement"]

    def create(self, validated_data):
        Password = validated_data.pop('Password', None)
        instance = self.Meta.model(**validated_data)
        if Password is not None:
            instance.Password = make_password(Password) # Encryted the Password
        instance.save()
        return instance

class CheckInSerializer(serializers.ModelSerializer):

    FullName = serializers.CharField(write_only=True) # Define a new field FullName which will be write-only, meaning it will be used for input only and won't be included in the output

    class Meta:
        model = CheckIn
        fields = ["id", 'FullName', 'Location', 'Latitude', 'Longitude','CheckIn_time']

        """
        The user__username=value is used because the Employee model has a OneToOneField relationship with the User model, 
        and the User model has a username field.

        When you use the double underscore __, Django's ORM allows you to traverse the relationship. 
        So user__username means you are accessing the username field of the User model through the 
        user relationship on the Employee model.
        """

    def validate_FullName(self, value):
        if not Employee.objects.filter(user__FullName=value).exists(): 
            # user = models.OneToOneField(User, on_delete=models.CASCADE)
            # user__FullName: because the Employee model has the OntoMany ralationships to the User Modle that name user in Employee model
            raise serializers.ValidationError("Employee does not exist")
        return value
    

    def create(self, validated_data):
        FullName = validated_data.pop('FullName') # Extract the FullName from the validated data
        employee = Employee.objects.get(user__FullName=FullName) # Find the Employee object that matches the FullName
        check_in = CheckIn.objects.create(employee=employee, **validated_data) #create the instance to the CheckIn Model
        return check_in
    
class ProfileSerialize(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'Email', 'Address', 'City','Postcode', 'Role']


class CheckIn_infoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckIn
        fields = ["id", "Location", "Latitude", "Longitude", "CheckIn_time"]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "customer", "contract_manager", 'employee', "Activate"]


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "Sender", "Receiver", "Workplace","Order_items", "Order_time", "Order_status"]

class ConversationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conversation
        fields = ["id", "Sender", "Receiver", "Message", "Sendingtime", "Image"]
