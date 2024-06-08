import config
from django.shortcuts import render
from openai import OpenAI
from django.http import JsonResponse
from .models import Chat

client = OpenAI(api_key=config.OPENAI_API_KEY)

# Create your views here.
def index(request):
    return render(request, 'index.html')

def response(request):
    if request.method == 'POST':
        message = request.POST.get('message', '')

        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message}
            ]
        )

        answer = completion.choices[0].message.content
        new_chat = Chat(message=message, response=answer)
        new_chat.save()
        return JsonResponse({'response': answer})
    return JsonResponse({'response': 'Invalid request'}, status=400)