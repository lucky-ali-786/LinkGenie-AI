import requests
from google import genai
import json
import subprocess
import os
from google.genai import types
from dotenv import load_dotenv
load_dotenv() 
client = genai.Client(api_key=os.getenv("APIKEY"))
import requests
from accestoken import accesstoken
def get_linkedin_urn() -> str:
    """Fetches your unique User URN from LinkedIn."""
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {
        "Authorization": f"Bearer {os.getenv("ACCESS_TOKEN")}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
     
        user_urn = response.json().get("sub")
        return user_urn
    else:
        raise Exception(f"Failed to fetch URN. Status: {response.status_code}, Error: {response.text}")
def upload_image_to_linkedin(image_path: str,user_urn: str) -> str:
    """
    Registers an upload and sends the image file to LinkedIn.
    Returns the Asset URN needed to attach the image to a post.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found at {image_path}")
    access_token=os.getenv("ACCESS_TOKEN")
    # 1. Register the upload
    register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": f"urn:li:person:{user_urn}",
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent"
                }
            ]
        }
    }
    register_response = requests.post(register_url, headers=headers, json=register_payload, timeout=15)
    if register_response.status_code != 200:
        raise Exception(f"Failed to register upload: {register_response.text}")
    data = register_response.json()
    upload_url = data['value']['uploadMechanism']['com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest']['uploadUrl']
    asset_urn = data['value']['asset']
    with open(image_path, 'rb') as image_file:
        image_data = image_file.read()
    upload_headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/octet-stream" 
    }
    
    upload_response = requests.put(upload_url, headers=upload_headers, data=image_data, timeout=30)
    
    if upload_response.status_code != 201:
        raise Exception(f"Failed to upload image bytes: {upload_response.text}")
        
    return asset_urn


def post_text_and_image_to_linkedin(text: str, asset_urn: str,user_urn: str) -> str:
    """
    Publishes a post with text and an attached image asset.
    """
    access_token=os.getenv("ACCESS_TOKEN")
    url = "https://api.linkedin.com/v2/ugcPosts"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json"
    }
    
    payload = {
        "author": f"urn:li:person:{user_urn}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {
                    "text": text
                },
                "shareMediaCategory": "IMAGE", 
                "media": [
                    {
                        "status": "READY",
                        "description": {"text": "Image description for accessibility"},
                        "media": asset_urn,
                        "title": {"text": "Image Title"}
                    }
                ]
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=15)
    
    if response.status_code == 201:
        post_id = response.json().get('id')
        return f"Successfully posted with image! Post ID: {post_id}"
    else:
        return f"Failed to post. Status: {response.status_code}, Error: {response.text}"
def run_command(command: str) -> str:
    """Executes a command in the terminal and returns the output. Use this to access or create files."""
    result = subprocess.getoutput(command)
    return result


# ------------------------------------------------------------------------------------------------------------

system_prompt = """
You are an autonomous, professional LinkedIn Social Media Agent.
Your objective is to draft engaging LinkedIn posts and publish them alongside a specific image using the provided tools.

The user will provide you with two things in their prompt:
1. The topic or raw notes for the post.
2. The exact filename of the image to attach.

You MUST strictly follow this workflow in order:
 WORKFLOW:
1. LOCATE IMAGE: Use the `run_command` tool to search the local file system and find the EXACT absolute path of the provided image filename (e.g., Use `dir /s /b filename.ext` on Windows). DO NOT guess or hallucinate the path.
2. GET AUTHORIZATION: Call the `get_linkedin_urn` tool to retrieve the user's unique URN. You will need this string for the subsequent steps.
3. DRAFT POST: Write a concise, highly readable LinkedIn post based on the user's topic. Keep it professional, well-spaced, and include 2-3 relevant hashtags.
4. UPLOAD IMAGE: Pass the absolute image path (from Step 1) and the `user_urn` (from Step 2) into the `upload_image_to_linkedin` tool. This tool will return an Asset URN.
5. PUBLISH POST: Pass your drafted text (from Step 3), the Asset URN (from Step 4), and the `user_urn` (from Step 2) into the `post_text_and_image_to_linkedin` tool to publish the final post.
 STRICT RULES:
- Never proceed to Step 4 if the `run_command` tool cannot find the image. Inform the user immediately.
- Never hallucinate the `user_urn` or the Asset URN. You must use exactly what the tools return.
- Do not ask the user for an access token or authentication details; assume the system handles backend authentication securely.
"""
chat = client.chats.create(
    model="gemini-2.5-flash", 
    config=types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.2, 
        tools=[get_linkedin_urn,upload_image_to_linkedin,post_text_and_image_to_linkedin,run_command]
    )
)
print("AI Agent initialized. Type 'exit' to quit.")
while True:
    inp = input("\nEnter your prompt: ")
    if inp.lower() == 'exit':
        break
    response = chat.send_message(inp)
    print(f"\nAI Agent:\n{response.text}")
    print("-" * 40)
