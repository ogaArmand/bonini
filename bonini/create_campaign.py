import requests
import json

url = "https://apis.letexto.com/v1/campaigns"

payload = json.dumps({
  "label": "My Campaign publipostage",
  "sender": "SMS INFO",
  "contacts": [
    {
      "age": "12",
      "numero": "2250000000000",
      "name": "Martial"
    },
    {
      "age": "24",
      "numero": "2250000000000",
      "name": "Rita"
    },
    {
      "age": "32",
      "numero": "2250000000000",
      "name": "John"
    }
  ],
  "content": "Hello {{name}}, votre numéro est {{numero}}"
})
headers = {
  'Authorization': 'Bearer <YOUR_TOKEN>',
  'Content-Type': 'application/json'
}

response = requests.post(url, data=payload, headers=headers)
data = response.json()
print(json.dumps(data))
