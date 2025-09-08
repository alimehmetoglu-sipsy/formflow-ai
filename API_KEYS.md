# API Keys Configuration

**IMPORTANT**: Never commit real API keys to GitHub. Replace placeholders in deployment scripts before running.

## Required API Keys

1. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Replace `YOUR_OPENAI_API_KEY_HERE` in scripts

2. **LemonSqueezy API Key**
   - Get from: https://app.lemonsqueezy.com/settings/api
   - Replace `YOUR_LEMONSQUEEZY_API_KEY_HERE` in scripts

3. **Resend API Key**
   - Get from: https://resend.com/api-keys
   - Replace `YOUR_RESEND_API_KEY_HERE` in scripts

## How to Use

1. Copy the actual API keys from your secure storage
2. When running deployment scripts in Google Cloud Shell:
   - Edit the script first
   - Replace placeholder values with actual keys
   - Run the script
   - Never commit the modified script back to GitHub

## Security Notes

- Store API keys in Google Secret Manager for production
- Use environment variables for local development
- Never hardcode API keys in source code
- Rotate keys regularly