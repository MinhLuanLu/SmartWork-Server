from django.http import HttpResponse, JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from .models import User, Employee, Manager,CheckIn,Assignment,Customer,Order, Conversation
from .serializers import UserSerializer, CheckInSerializer, ProfileSerialize, CheckIn_infoSerializer, AssignmentSerializer,OrderSerializer,ConversationSerializer

from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth.hashers import check_password







def home(request):
    return HttpResponse('HOME PAGE')

@api_view(['GET', 'POST'])
def register_api(request):
    if request.method == "GET":
        user = User.objects.all()
        userserializer = UserSerializer(user, many=True)
        
        return Response(userserializer.data)
    
    elif request.method == "POST":
        userserializer = UserSerializer(data=request.data)
        email = request.data.get('Email')
        role = request.data.get('Role')
            
        if User.objects.filter(Email=email).exists(): # Check the Emain is already in Database
            print("Email is already registered")
            return Response({'message': "Email is already registered"}, status=status.HTTP_400_BAD_REQUEST)
        if userserializer.is_valid():
            
            user = userserializer.save() #Save instance to User Model
            if role == "Employee":
                Employee.objects.create(user=user, Role=user.Role) # Save the instance to Employee Model
                
            elif role == "Manager":
                    Manager.objects.create(user=user, Role=user.Role)

            return Response({"message": "Registration successful"}, status=status.HTTP_201_CREATED)
        return Response({"message": "Data is not valid", "error": userserializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST', 'GET'])
def login(request):
    if request.method == "POST":
        Email = request.data.get('Email')
        Password = request.data.get('Password')

        user = User.objects.filter(Email=Email).first() # user first because the email is unique
        if user is None:
            raise AuthenticationFailed('User not found!')
        
        if not check_password(Password, user.Password):
            raise AuthenticationFailed('Incorrect password!')
        
        
        return Response({"message": "Login successful", "FullName": user.FullName, "user_role": user.Role}, status=status.HTTP_200_OK)

@api_view(["POST", "GET"])
def api_CheckIn(request):
   if request.method == "GET":
       checIn = CheckIn.objects.all()
       checkInSerializer = CheckInSerializer(checIn, many=True)
       return Response(checkInSerializer.data)
   
   if request.method == "POST":
        serializer = CheckInSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "CheckIn successful"}, status=status.HTTP_201_CREATED)
        return Response({"massage": "Data is not valid", 'error': "Error from Server"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(["POST", "GET"]) #Do not to save the data to database
def api_User_info(request):
    if request.method == "GET":
        user_info = User.objects.all()
        profileserializer = ProfileSerialize(user_info, many=True)
        return Response(profileserializer.data) 
    
    if request.method == 'POST':
       Email = request.data.get('Email') #get the object Email in the API POST from Forntend
       info = User.objects.filter(Email=Email).first() # Get the Email in User Model [User.objects.get(Email=Email)]

       if info is None: 
            return Response({"error": 'Data is not valid'}, status=status.HTTP_400_BAD_REQUEST)
       
       profileserializer = ProfileSerialize(info) #Get all the data match that match the Email
    return Response({"message": 'successful', "user_info": profileserializer.data}, status=status.HTTP_200_OK)
    

@api_view(["POST"])
def CheckIn_info_api(request):
    
    if request.method == 'POST':
        get_email = request.data.get('Email')
        
        employee_check_info = CheckIn.objects.filter(employee__user__Email = get_email) # Get the Email in User Model by using __
        employee_check_infoSerializer = CheckIn_infoSerializer(employee_check_info, many=True) # Make the data to Serializer fields
    
        if employee_check_info is None:
            return Response({"message": "data not vailid"}, status=status.HTTP_400_BAD_REQUEST)
         
        get = employee_check_infoSerializer.data

        
        return Response({"message": "Did Get Data", "checkin_info": get}, status=status.HTTP_200_OK)
    

@api_view(['GET', 'POST'])
def api_Assignment(request):
    if request.method == "GET":
        assignment = Assignment.objects.all()
        assignmentSerializer = AssignmentSerializer(assignment, many=True)
        return Response(assignmentSerializer.data)
    
    if request.method == "POST":
        email = request.data.get("Email")
        data = request.data.get("Search_data")

        
        check_email_employee = Assignment.objects.filter(employee__user__Email = email) 
        search_data = data.capitalize() # maake the first letter is capitalized

        check_email_manager = Assignment.objects.filter(contract_manager__user__Email = email)
       
      
        if  not check_email_employee and not check_email_manager:
            return Response({"message": " Email is not vailid"}, status=status.HTTP_400_BAD_REQUEST) #### Need to change
        try:
            check_customer_name = Assignment.objects.get(customer__CustomerName=search_data)
        except Assignment.DoesNotExist:
            return Response({"message": "Your Workplace is not exist in the system ! Try again."}, status=status.HTTP_400_BAD_REQUEST)
        
        ## send error massage to frontend if check email and check data search not exist
        print(f"{email} Searching for: {search_data}")
        
        assignmentSerializer = AssignmentSerializer(check_customer_name)
        print(f"Result: {assignmentSerializer.data}")
        get_contract_manager_id = assignmentSerializer.data['contract_manager']
        get_customer_id = assignmentSerializer.data["customer"]
        get_employee_id = assignmentSerializer.data["employee"]

        contract_manager_list = []
        customer_list = []
        employee_list = []

        try:
            for i in get_contract_manager_id:
                user = Manager.objects.get(id=i)
                manager_name = user.user.FullName  #In the Manager has user => FullName feilds

                contract_manager_list.append(manager_name)

            for i in get_employee_id:
                employee = Employee.objects.get(id=i)
                employee_name = employee.user.FullName

                employee_list.append(employee_name)

            for i in get_customer_id:
                customer = Customer.objects.get(id=i)
                customer_name = customer.CustomerName
                customer_list.append(customer_name)

        
        except Manager.DoesNotExist:
            return Response({"message": "User ID is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        
        info = {"contract_manager": contract_manager_list, "employee": employee_list, "customer": customer_list}
        return Response({"message": "Get data complete...", "contract_manager": contract_manager_list, "employee": employee_list, "customer": customer_list, "info": info}, status=status.HTTP_200_OK)
    
@api_view(['GET', "POST"])
def Workplace(request):
    if request.method == "GET":
        assignment = Assignment.objects.all()
        assignmentSerializer = AssignmentSerializer(assignment, many=True)
        return Response(assignmentSerializer.data)
    
    if request.method == "POST":
        name = request.data.get('FullName')
        if not name:
            return Response({'message': "FullName not provided"}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if an employee with the given name exists
        check_name = Assignment.objects.filter(employee__user__FullName=name)
  
       
        if not check_name.exists():
            return Response({'message': "The Employee name is not in the system"}, status=status.HTTP_400_BAD_REQUEST)
            
        
        
        # Check if there is any customer associated with the employee
        customers = Customer.objects.filter(assignment__employee__user__FullName=name)
        if not customers.exists():
            return Response({'message': "No customers found for the given employee"}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the customer names
        customer_names = customers.values_list('CustomerName', flat=True)
        return Response({"message": "Got Workplace Name...", "workplaces": list(customer_names)}, status=status.HTTP_200_OK)
    

@api_view(['GET', "POST"])
def api_Get_Manager(request):
    if request.method == "GET":
        assignment = Assignment.objects.all()
        assignmentSerializer = AssignmentSerializer(assignment, many=True)
        return Response(assignmentSerializer.data)
    
    if request.method == "POST":
        name = request.data.get('FullName')
        if not name:
            return Response({'message': "FullName not provided"}, status=status.HTTP_400_BAD_REQUEST)
       
        # Check if an employee with the given name exists
        check_name = Assignment.objects.filter(contract_manager__user__FullName=name)
  
       
        if not check_name.exists():
            return Response({'message': "The Employee name is not in the system"}, status=status.HTTP_400_BAD_REQUEST)
            
        
        
        # Check if there is any customer associated with the employee
        customers = Customer.objects.filter(assignment__contract_manager__user__FullName=name)
        if not customers.exists():
            return Response({'message': "No customers found for the given employee"}, status=status.HTTP_404_NOT_FOUND)
        
        # Return the customer names
        customer_names = customers.values_list('CustomerName', flat=True)
        return Response({"message": "Got Workplace Name...", "workplaces": list(customer_names)}, status=status.HTTP_200_OK)
        

    
@api_view(["GET", "POST"])
def api_Order(request):
    if request.method == "GET":
        order = Order.objects.all()
        orderserializer = OrderSerializer(order, many=True)
        return Response(orderserializer.data)
    
    if request.method == "POST":
        sender = request.data.get('Sender')
        receiver = request.data.get("Receiver")
        getworkplace = request.data.get('Workplace')
        order_items = request.data.get("Order_items")

        manager_name = request.data.get('FullName')


        workplace = getworkplace
        print(f"Sender [{sender}] Ordering from {workplace} to {receiver} [{order_items}]")

        try:
            check_customer_name = Assignment.objects.get(customer__CustomerName=workplace)
        except Assignment.DoesNotExist:
            return Response({"message": "Your Workplace is not exist in the system ! Try again."}, status=status.HTTP_400_BAD_REQUEST)
        
        assignmentSerializer = AssignmentSerializer(check_customer_name)
        
        get_contract_manager_id = assignmentSerializer.data['contract_manager']
        get_customer_id = assignmentSerializer.data["customer"]
        get_employee_id = assignmentSerializer.data["employee"]

        contract_manager_list = []
        customer_list = []
        employee_list = []

        try:
            for i in get_contract_manager_id:
                user = Manager.objects.get(id=i)
                manager_name = user.user.FullName  #In the Manager has user => FullName feilds

                contract_manager_list.append(manager_name)

            for i in get_employee_id:
                employee = Employee.objects.get(id=i)
                employee_name = employee.user.FullName

                employee_list.append(employee_name)

            for i in get_customer_id:
                customer = Customer.objects.get(id=i)
                customer_name = customer.CustomerName
                customer_list.append(customer_name)

            
        except Manager.DoesNotExist:
            return Response({"message": "User ID is not valid"}, status=status.HTTP_400_BAD_REQUEST)
        
        for manager in contract_manager_list:
            if receiver == manager:
                break

            else:
                return Response({"message": "Can't send your order"}, status=status.HTTP_400_BAD_REQUEST)
            
        orderserializer = OrderSerializer(data=request.data)
        if orderserializer.is_valid():
            orderserializer.save()
            return Response({"message": "Your order has been sent to your Manger."}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Error: Can't save your order to system. Please try again."}, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(["POST", "GET"])
def api_Requestments(request):
    if request.method == 'GET':
        order = Order.objects.all()
        orderserializer = OrderSerializer(order, many=True)
        return Response(orderserializer.data)
    
    if request.method == 'POST':
        get_fullname = request.data.get('FullName')
        get_order_status = request.data.get('Status')
       

        check_receiver_name = Order.objects.filter(Receiver=get_fullname)
        check_sender_name = Order.objects.filter(Sender=get_fullname)
        check_order_status_manager = Order.objects.filter(Receiver=get_fullname,Order_status = get_order_status)
        check_order_status_employee = Order.objects.filter(Sender = get_fullname, Order_status = get_order_status)

        if not check_receiver_name.exists:   
             return Response({"message": f'Couldnt found the receiver [{get_fullname}] in the system, Please try logout and again' }, status=status.HTTP_400_BAD_REQUEST)
        if not check_order_status_manager and  not check_order_status_employee:
            return Response({"message": "No orders are available.."}, status=status.HTTP_400_BAD_REQUEST)
        
        if check_order_status_manager:
            orderSerializer = OrderSerializer(check_order_status_manager, many=True) # Just get all the orders has waiting status
            return Response({'message': orderSerializer.data}, status=status.HTTP_200_OK)
        
        if check_order_status_employee:
            orderSerializer = OrderSerializer(check_sender_name, many=True) ## Get all the orders that match the Sender name
            return Response({'message': orderSerializer.data}, status=status.HTTP_200_OK)


@api_view(["POST", "GET"])
def Approved_order_api(request):
    if request.method == "GET":
        order = Order.objects.all()
        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)
    
    if request.method == "POST":
        sender = request.data.get('Sender')
        receiver = request.data.get('Receiver')
        order_time = request.data.get('Order_time')
        order_status = request.data.get('Order_status')
        new_status = 'Approved'
        

        check_order_approved = Order.objects.filter(Sender = sender, Receiver = receiver, Order_time = order_time, Order_status = order_status)
        if not check_order_approved.exists():
            return Response({"message": "Error to Approved the order. please try again.."}, status=status.HTTP_400_BAD_REQUEST)

        check_order_approved.update(Order_status=new_status)
        return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)
    

@api_view(["POST", "GET"])
def Decline_order_api(request):
    if request.method == "GET":
        order = Order.objects.all()
        orderSerializer = OrderSerializer(order, many=True)
        return Response(orderSerializer.data)
       
    if request.method == "POST":
        sender = request.data.get('Sender')
        receiver = request.data.get('Receiver')
        order_time = request.data.get('Order_time')
        order_status = request.data.get('Order_status')
        new_status = 'Decline'
        

        check_order_approved = Order.objects.filter(Sender = sender, Receiver = receiver, Order_time = order_time, Order_status = order_status)
        if not check_order_approved.exists():
            return Response({"message": "Error to Approved the order. please try again.."}, status=status.HTTP_400_BAD_REQUEST)

        check_order_approved.update(Order_status=new_status)
        return Response({"message": "Order status updated successfully"}, status=status.HTTP_200_OK)
        
@api_view(['GET', 'POST'])
def api_Conversation(request):
    if request.method == 'GET':
        conversation = Conversation.objects.all()
        serializer = ConversationSerializer(conversation, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        message = ConversationSerializer(data=request.data)
        Sender = request.data.get('Sender')
        Receiver = request.data.get('Receiver')
        Image = request.data.get('Image')
        check_sender = Conversation.objects.filter(Sender=Sender, Receiver=Receiver)
        


        if message.is_valid():
            message.save()
        print(Image)
        serializer = ConversationSerializer(check_sender,many=True)
        return Response({"message": "Message has been sent", "conversation": serializer.data})


@api_view(['GET', 'POST'])
def api_Get_Conversation(request):
    if request.method == 'GET':
        conversation = Conversation.objects.all()
        serializer = ConversationSerializer(conversation, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        Sender = request.data.get('Sender')
        Receiver = request.data.get('Receiver')

        check_receiver = Conversation.objects.filter(Sender=Receiver, Receiver=Sender)

        serializer = ConversationSerializer(check_receiver,many=True)
        return Response({"message": "Message has been sent", "conversation": serializer.data})

        
        

    

        
        
        