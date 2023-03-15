import requests
import json
import time

# You can obtain your LEAP_API-KEY from https://www.tryleap.ai/
API_KEY = "add-your-API-KEY-here"

# Authorization dictionary
HEADERS = {
    "accept": "application/json",
    "content-type": "application/json",
    "authorization": f"Bearer {API_KEY}"
}

IMAGES = [
    "https://nation-media-assets.storage.googleapis.com/wp-content/uploads/2022/05/25182332/peter-obi1.jpg",
    "https://www.primebusiness.africa/wp-content/uploads/2022/12/peter-obi.jpg",
    "https://cdn.vanguardngr.com/wp-content/uploads/2022/10/Peter-Obi-011.png"
]


def create_model(title):
    url = "https://api.tryleap.ai/api/v1/images/models"
    payload = {
        "title": title,
        "subjectKeyword": "@draft"
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    model_id = json.loads(response.text)["id"]
    return model_id


def upload_image_samples(model_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/samples/url"
    payload = {"images": IMAGES}
    response = requests.post(url, json=payload, headers=HEADERS)
    # No need to save the response as it's not used later
    # Some error checking here would be nice to have


def queue_training_job(model_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/queue"
    response = requests.post(url, headers=HEADERS)
    data = json.loads(response.text)

    version_id = data["id"]
    status = data["status"]

    print(f"Version ID: {version_id}. Status: {status}")
    return version_id, status


def get_model_version(model_id, version_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/versions/{version_id}"
    response = requests.get(url, headers=HEADERS)
    data = json.loads(response.text)

    version_id = data["id"]
    status = data["status"]

    print(f"Version ID: {version_id}. Status: {status}")
    return version_id, status


def generate_image(model_id, prompt):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences"
    payload = {
        "prompt": prompt,
        "steps": 50,
        "width": 512,
        "height": 512,
        "numberOfImages": 1,
        "seed": 4523184
    }
    response = requests.post(url, json=payload, headers=HEADERS)
    data = json.loads(response.text)

    inference_id = data["id"]
    status = data["status"]

    print(f"Inference ID: {inference_id}. Status: {status}")

    if status != "finished":
        raise Exception("Inference Job did not finish")

    return inference_id, status


def get_inference_job(model_id, inference_id):
    url = f"https://api.tryleap.ai/api/v1/images/models/{model_id}/inferences/{inference_id}"

    response = requests.get(url, headers=HEADERS)
    data = json.loads(response.text)

    inference_id = data["id"]
    state = data["state"]
    image = None

    if len(data["images"]):
        image = data["images"][0]["uri"]

    print(f"Inference ID: {inference_id}. State: {state}")

    return inference_id, state, image


# Creating a custom model for the fine-tuning step
model_id = create_model("Sample")

#Upload the items in IMAGES for fine-tuning
upload_image_samples(model_id)

#This step Fine-tunes the trained model
version_id, status = queue_training_job(model_id)
while status != "finished":
    time.sleep(10)
    version_id, status = get_model_version(model_id, version_id)

#Image generation step. Note to include the necessary keywords in the prompt variable
inference_id, status = generate_image(
    model_id, 
    prompt="A photo of @draft with a face cap and cute face in a tech face"
)
while status != "finished":
    time.sleep(10)
    inference_id, status, image = get_inference_job(model_id, inference_id)

print(image)
