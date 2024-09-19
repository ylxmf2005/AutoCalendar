import requests
import webbrowser

url = "http://localhost:8000/upload_from_shortcut"

image_file_path = "./uploads/input.png"

data = {
    'calendar': 'iCloud',  
    'startDate': '2024-09-02'  
}

with open(image_file_path, 'rb') as image_file:
    files = {'image': image_file}
    
    response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    print("Image uploaded successfully!")
    response_json = response.json()

    if 'url' in response_json:
        generated_url = response_json['url']
        print(f"Opening URL: {generated_url}")
        
        webbrowser.open(generated_url)
    else:
        print("Error: URL not found in the response.")
else:
    print(f"Failed to upload image. Status code: {response.status_code}")
    print("Response text:", response.text)
