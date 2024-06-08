import config
import time
from django.shortcuts import render
from django.http import JsonResponse
from openai import OpenAI
from openai import RateLimitError, OpenAIError


client = OpenAI(api_key=config.OPENAI_API_KEY)

def index(request):
  return render(request, 'index.html')

def create_completion_with_retry(message, retries=2):
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ])
            return completion
        except RateLimitError:
            if attempt < retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                time.sleep(wait_time)
            else:
                raise
        except OpenAIError as e:
            raise

def response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')
        try:
            completion = create_completion_with_retry(message)
            answer = completion.choices[0].message.content  # Updated to match new API response structure
            return JsonResponse({'response': answer})
        except RateLimitError:
            return JsonResponse({'error': 'Rate limit exceeded. Please try again later.'}, status=429)
        except OpenAIError as e:
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            return JsonResponse({'error': 'An unexpected error occurred.'}, status=500)
    return JsonResponse({'response': 'invalid request'}, status=400)

