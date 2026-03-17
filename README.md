# LinkGenie AI 🤖🔗

**GitHub Description:** An LLM-driven bot that automates LinkedIn interactions, allowing users to seamlessly generate content, upload images, and publish posts directly using secure environment variables and dynamic prompts.

## 🚀 Features

* **LLM-Powered Content Generation:** Dynamically generate engaging LinkedIn posts using prompts.
* **Automated Image Uploads:** Built-in functions for the LLM to upload images to LinkedIn's servers.
* **Direct Publishing:** Seamlessly publish text and image posts to your profile.
* **Secure Token Management:** Uses a `.env` file for secure access token storage—no hardcoding required.
* **Dynamic User Routing:** Pass the `user_urn` directly through the prompt for flexible, context-aware posting.

## 🛠️ Tech Stack

* **Language:** JavaScript (Node.js) / Python
* **LLM Integration:** Gemini API / OpenAI
* **Environment Management:** dotenv

## 📦 Installation & Setup

```bash
git clone [https://github.com/yourusername/LinkGenie-AI.git](https://github.com/yourusername/LinkGenie-AI.git)
cd LinkGenie-AI
npm install 
# or pip install -r requirements.txt if using Python

# Create a .env file in the root directory and add these variables:
# LINKEDIN_ACCESS_TOKEN=your_linkedin_access_token_here
# LLM_API_KEY=your_llm_api_key_here
