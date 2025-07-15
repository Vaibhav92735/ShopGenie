<<<<<<< HEAD
# import requests

# url = "http://localhost:8000/process-text/"
# data = {
#     "username": "vaibhav123",
#     "user_query": "Show the cart"
# }

# response = requests.post(url, data=data)
# print(response.json())

# import requests

# url = "http://localhost:8000/process-image/"
# files = {'image': open('shopping_list.jpg', 'rb')}
# data = {'username': 'vaibhav123'}

# response = requests.post(url, files=files, data=data)
# print(response.json())

import requests

# Set the endpoint URL (adjust if using ngrok or running elsewhere)
url = "http://127.0.0.1:8000/process-voice/"

# Set the path to your audio file
audio_path = "../data/sampleAudio.mp3"  # Replace with your actual file path

# Set the username
username = "vaibhav"

# Prepare the multipart-form data
files = {
    "audio": open(audio_path, "rb")
}
data = {
    "username": username
}

# Make the POST request
response = requests.post(url, data=data, files=files)

# Print the response
print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Error decoding JSON:", e)
=======
# import requests

# url = "http://localhost:8000/process-text/"
# data = {
#     "username": "vaibhav123",
#     "user_query": "Show the cart"
# }

# response = requests.post(url, data=data)
# print(response.json())

# import requests

# url = "http://localhost:8000/process-image/"
# files = {'image': open('shopping_list.jpg', 'rb')}
# data = {'username': 'vaibhav123'}

# response = requests.post(url, files=files, data=data)
# print(response.json())

import requests

# Set the endpoint URL (adjust if using ngrok or running elsewhere)
url = "http://127.0.0.1:8000/process-voice/"

# Set the path to your audio file
audio_path = "../data/sampleAudio.mp3"  # Replace with your actual file path

# Set the username
username = "vaibhav"

# Prepare the multipart-form data
files = {
    "audio": open(audio_path, "rb")
}
data = {
    "username": username
}

# Make the POST request
response = requests.post(url, data=data, files=files)

# Print the response
print("Status Code:", response.status_code)
try:
    print("Response JSON:", response.json())
except Exception as e:
    print("Error decoding JSON:", e)
>>>>>>> 949aed019984cffe3a7d9b73912ce184636018fd
    print("Raw Response:", response.text)