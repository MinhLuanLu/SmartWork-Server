from django.db import models




class User(models.Model):
    FullName = models.CharField(max_length=50)
    Email = models.EmailField(max_length=50, unique=True)
    Address = models.CharField(max_length=100)
    City = models.CharField(max_length=50)
    Postcode = models.CharField(max_length=8)
    Password = models.CharField(max_length=50)
    Policy_agreement = models.BooleanField()
    Role = models.CharField(max_length=50, default='Employee')
    Joined_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.FullName
    


class Employee(models.Model):
    Role = models.CharField(max_length=50, default='Employee')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        info = f"{self.user.FullName}"
        return info

class Manager(models.Model):
    Role = models.CharField(max_length=50, default='Employee')
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        info = f"{self.user.FullName}"
        return info
    
class Customer(models.Model):
    CustomerName = models.CharField(max_length=100)
    Address = models.CharField(max_length=50)
    Country = models.CharField(max_length=50)
    City = models.CharField(max_length=50)
    Contract_Number = models.CharField(max_length=50)
    Due_date = models.DateField()
    Created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.CustomerName


class Assignment(models.Model):
    Titlle = models.CharField(max_length=100)
    Description = models.TextField()
    customer = models.ManyToManyField(Customer)
    contract_manager = models.ManyToManyField(Manager)
    employee = models.ManyToManyField(Employee)
    Created_at = models.DateField(auto_now_add=True)
    Activate = models.BooleanField()

    def __str__(self):
        info = f'{self.Titlle}: {self.Created_at} [ Status: Active ]'
        if self.Activate == True:
            return info
        else:
            info = f'{self.Titlle}: {self.Created_at} [ Status: Cancelled ]'

class CheckIn(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    Location = models.CharField(max_length=100)
    Latitude = models.CharField(max_length=50)
    Longitude = models.CharField(max_length=50)
    CheckIn_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.user.FullName} - CheckIn at [ {str(self.CheckIn_time)} - {self.Location}]"
    

class Order(models.Model):
    Sender = models.CharField(max_length=100)
    Receiver = models.CharField(max_length=100)
    Workplace = models.CharField(max_length=100)
    Order_items = models.CharField(max_length=1000)
    Order_time = models.CharField(max_length=100)
    Order_status = models.CharField(max_length=100)
    Time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sender [{self.Sender}] Ordering from {self.Workplace} to {self.Receiver} - {self.Time}"


class Conversation(models.Model):
    Sender = models.CharField(max_length=100)
    Receiver = models.CharField(max_length=100,)
    Message = models.CharField(max_length=1000000, blank=True)
    Sendingtime = models.CharField(max_length=100)
    Image = models.ImageField(upload_to='conversation/Images', blank=True)

    def __str__(self):
        return f"Sender [{self.Sender} - Receiver [{self.Receiver}] - Sendingtime [{self.Sendingtime}]"