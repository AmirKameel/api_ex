import requests

base_url = "http://localhost:5000/parse-pdf"

# Prepare the file to send with the POST request
files = {'pdf': open('manual.pdf', 'rb')}
params = {'expand_pages': 7}  # Optional, if you want to specify the number of pages to expand

# Send the POST request
response = requests.post(base_url, files=files, data=params)

# Print the response
print(response.json())

# Close the file after the request
files['pdf'].close()
