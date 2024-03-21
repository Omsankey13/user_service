from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import user_details
from .serializers import serializer_user
import time
from functools import wraps
from rest_framework.decorators import api_view



def measure_execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Execution time of {func.__name__}: {execution_time:.4f} seconds")
        return result
    return wrapper


@api_view(['POST'])
@csrf_exempt
@measure_execution_time
def create_user(request):
    try:
        
        if type(request) != dict:
            request_data = json.loads(request.body)
        else:
            request_data = request
        
        serializer = serializer_user(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({"message":"User created successfully!!","data":serializer.data},status=201)
        else:
            return JsonResponse({"message":"Invalid Data Provided"})
        
    except Exception as error:
        return JsonResponse({"message":"Something went wrong","error":str(error)},status=500)
    
@api_view(['GET'])
@csrf_exempt
@measure_execution_time
def read_user(request,pk):
    try:
        user = user_details.objects.get(pk=pk,is_deleted=False)
        serializer = serializer_user(user)
        if serializer.data:
            return JsonResponse({"message":"User details retrieved successfully!!","data":serializer.data})
        else:
            return JsonResponse({"message":"NO data found"})  
    except Exception as error:
        print('read_user()',error)
        return JsonResponse({"message":"Something went wrong"},status=500)
    
@api_view(['GET'])
@csrf_exempt
@measure_execution_time
def get_all_user_list(request):
    try:
        user_object = user_details.objects.filter(is_deleted=False)
        serializer = serializer_user(user_object, many=True)
        if serializer.data:
            return JsonResponse({"message":"User details retrieved successfully!!","total":len(serializer.data),"data":serializer.data})
        else:
            return JsonResponse({"message":"No data found!!"})
    except Exception as error:
        print("get_all_user_list(): ", error)
        return JsonResponse({"message":"Something went wrong"},status=500)
   
 
@csrf_exempt
@measure_execution_time
def update_user(request, pk):
    try:
        user = user_details.objects.get(pk=pk)
        if request.method == 'PUT':
            if type(request) != dict:
                request_data = json.loads(request.body)
            serializer = serializer_user(user, data=request_data)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse({"message": "User updated successfully!!!", "data": serializer.data})
            else:
                return JsonResponse({"message": "Invalid data provided", "errors": serializer.errors}, status=400)
        else:
            return JsonResponse({"message": "Invalid HTTP method"}, status=405)
    
    except Exception as error:
        print('update_user()',error)
        return JsonResponse({"message": "Something went wrong"}, status=500)
 
 
@csrf_exempt
@measure_execution_time
def delete_user(request, pk):
    try:
        user = user_details.objects.get(pk=pk)
        if request.method == 'DELETE':
            user.delete()
            return JsonResponse({"message": "User deleted successfully!!!"})
        else:
            return JsonResponse({"message": "Invalid HTTP method"}, status=405)
    except Exception as error:
        print("delete_user()",error)
        return JsonResponse({"message": "Something went wrong", "error": str(error)}, status=500)


# Interservice Call for getting vehicle details from user_id
import requests
from rest_framework.decorators import api_view

@api_view(['GET'])
@csrf_exempt
def get_user_details_by_id_with_all_vehicles(request):
    try:
        user_id = request.GET.get('user_id')  
        if user_id:
            print(user_id)
            user_object = user_details.objects.filter(user_id=user_id, is_deleted=False)
            # user = user_details.objects.get(user_id=user_id, is_deleted=False)
            print(user_details)
            # print(user)

            serializer = serializer_user(user_object)
            print(serializer.data)
            
            if user_object.exists():
                print(user_id)
                # INterservice call to get vehicle data for user_id..
                vehicle_response = requests.get("http://localhost:6000/api/get_vehicle_details_by_id",params={'user_id':user_id})
                vehicle_data=[]    
                if vehicle_response.status_code==200:
                    vehicle_data=vehicle_response.json().get('data',())
                data = {
                    "user_details":serializer.data, 
                    "vehicle_details":vehicle_data
                }
                return JsonResponse({"message": f"User details for {user_id} `retrieved successfully!!", "data": data})
            else:
                return JsonResponse({"message": f"No vehicle details found for {user_id}"})
        else:
            return JsonResponse({"message": "Date parameter is missing."}, status=400)
    except Exception as error:
        return JsonResponse({"message": "Something went wrong", "error": str(error)}, status=500)






import requests

from datetime import datetime
from django.core.paginator import Paginator
 
def get_vehicles_details_in_date_range(start_date,end_date,page_number):
    try:
 
        #parse
        start_date = datetime.strptime(start_date, '%d-%m-%Y')
        end_date = datetime.strptime(end_date, '%d-%m-%Y')
 
        #format the dates
        start_date_standard = start_date.strftime('%Y-%m-%d')
        end_date_standard = end_date.strftime('%Y-%m-%d')
 
        #params
        params = {'start_date': start_date_standard, 'end_date': end_date_standard}
 
        response = requests.get("http://localhost:6000/api/vehicle-service/get_vehicle_details_by_date_range",params=params)
 
        if response.status_code==200:
            data=response.json
            sorted_data = sorted(data['data'], key=lambda x: x['created_at'])
 
            paginator = Paginator(sorted_data, 5)  # 5 results per page
            page_obj = paginator.get_page(page_number)
           
            return page_obj.object_list
        else:
            return JsonResponse({"message": "Failed to fetch details"}, status=500)
       
    except Exception as error:
        print("Error",error)
        return None
    


#interservice call between user_service and vehicle__service based on the UTC format date 

import pytz
from django.utils import timezone

# def get_vehicle_details_in_UTC_date_range(start_date,end_date):
#     try:
#         start_date_standard=start_date.strftime('%d-%m-%y')
#         end_date_standard=end_date.strftime('%d-%m-%y')

#         # Check if the provided date has timezone information
#         if start_date_standard.tzinfo==pytz.utc and end_date_standard.tzinfo==pytz.utc:
#             params={'start_date':start_date_standard,'end_date':end_date_standard}
#             response=requests.get("http://localhost:6000/api/get_vehicle_details_by_UTC_date_range",params=params)

#             if response.status_code==200:
#                 data=response.json
#                 sorted_data = sorted(data['data'], key=lambda x: x['created_at'])
#                 return sorted_data

#         else:
#             return JsonResponse({"message":"Date format is not in UTC "})
        
        
        
        




    # except Exception as error:
    #     return None

def convert_utc_to_ist(utc_datetime):
    # Define UTC timezone
    utc_timezone = pytz.timezone('UTC')

    # Convert UTC datetime to IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_datetime = utc_datetime.astimezone(ist_timezone)

    return ist_datetime

def get_vehicles_details_in_date_range(request):
    try:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse start and end dates into datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Convert start and end dates to UTC datetime objects
        start_date_utc = start_date.replace(tzinfo=pytz.utc)
        end_date_utc = end_date.replace(tzinfo=pytz.utc)

        # Convert UTC datetime objects to IST timezone
        start_date_ist = convert_utc_to_ist(start_date_utc)
        end_date_ist = convert_utc_to_ist(end_date_utc)

        # Handle the rest of your logic here...
        
        return JsonResponse({"message": "Success", "start_date_ist": start_date_ist.strftime('%Y-%m-%d %H:%M:%S'), "end_date_ist": end_date_ist.strftime('%Y-%m-%d %H:%M:%S')})

    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)
    


@api_view(['GET'])
@csrf_exempt
def convert_utc_to_ist(utc_datetime):
    # Define UTC timezone
    utc_timezone = pytz.timezone('UTC')

    # Convert UTC datetime to IST timezone
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_datetime = utc_datetime.astimezone(ist_timezone)

    return ist_datetime

def get_vehicles_details_in_date_range(request):
    try:
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')

        # Parse start and end dates into datetime objects
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Convert start and end dates to UTC datetime objects
        start_date_utc = start_date.replace(tzinfo=pytz.utc)
        end_date_utc = end_date.replace(tzinfo=pytz.utc)

        # Convert UTC datetime objects to IST timezone
        start_date_ist = convert_utc_to_ist(start_date_utc)
        end_date_ist = convert_utc_to_ist(end_date_utc)

        # Handle the rest of your logic here...
        
        return JsonResponse({"message": "Success", "start_date_ist": start_date_ist.strftime('%Y-%m-%d %H:%M:%S'), "end_date_ist": end_date_ist.strftime('%Y-%m-%d %H:%M:%S')})

    except Exception as e:
        return JsonResponse({"message": "Error", "error": str(e)}, status=500)