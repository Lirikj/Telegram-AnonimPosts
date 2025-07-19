import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
from config import API_KEY

client = ChatCompletionsClient(
    endpoint="https://models.github.ai/inference",
    credential=AzureKeyCredential(API_KEY))




def chat_with_gpt(prompt):
    try:
        messages = [
            SystemMessage(content="""Вы — модератор анонимного канала.

Ваша задача — анализировать входящие сообщения и определять, можно ли их публиковать.

❌ Выведите False, если сообщение содержит:
– личные оскорбления (например: "он чмо", "тварь", "долбоёб"),
– уничижительные или пошлые высказывания о чьей-то сексуальной жизни, даже в форме слухов, шуток, намёков или домыслов (например: "она сосала", "он трахал её", "они переспали", "говорят, он гей", "она всем даёт"),
– любые подозрения, домыслы или слухи, затрагивающие честь, репутацию или личную жизнь других людей, даже без мата,
– прямые угрозы или агрессию (например: "я тебя найду", "убью", "разнесу").

✅ Выведите True, если сообщение:
– выражает эмоции, критику, мат, сарказм, иронию, но не касается чужой личной жизни,
– не содержит слухов, сплетен, унижений или угроз.

Выводите строго одно слово — True или False, без кавычек, без пояснений.

Запрещайте всё, что даже отдалённо может казаться унизительной сплетней или слухом.
"""),
            UserMessage(content=prompt)
        ]
        model_name = os.environ.get("AZURE_MODEL", "openai/gpt-4.1")
        response = client.complete(
            messages=messages,
            model=os.environ.get("AZURE_MODEL", "openai/gpt-4.1"),
            temperature=1.0,
            top_p=1.0)
        
        return response.choices[0].message.content
    except Exception as e:
        return "False"





