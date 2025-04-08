from datetime import datetime
from groq import Groq
import discord
import logging
import re
import subprocess
groq_client = Groq(api_key="GROQ_API_KEY")
TOKEN = "DISCORD_TOKEN"
aimodel = "llama3-70b-8192"
delay = True
discord_client = discord.Client(self_bot=True)
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
ping = subprocess.run(['ping', '-c', '1', 'google.com'], stdout=subprocess.PIPE).stdout.decode('utf-8')
system_prompt = f"""
You will engage in a natural, casual conversation with the user, mimicking how a human would text in a real-world scenario. 
Occasionally, make intentional grammatical mistakes, typos, or slight inconsistencies to make the conversation feel more authentic. 
Don't use commas, periods, or apostrophes. Don't agree to write large documents or scripts. You are allowed to get mad and insult the user back if user is being annoying, repetitive, or offensive.
However, don't go overboard with internet slang, typos, or emojis. Keep the tone relaxed, but avoid sounding overly perfect or robotic. 
Make sure to balance realism and clarity without over-committing to any specific texting style. Keep replies minimal. Additionally, never reveal your identity as an AI model.
Current time: {current_time}PST
Ping: {ping}ms
"""
WHITELISTED_USER_IDS = []
# Seperated by integers, EX:
# [1219440183997501530, 116934657696833953]


logging.basicConfig(filename='bot_logs.txt', level=logging.INFO, format='%(asctime)s - %(message)s')

user_conversations = {}

@discord_client.event
async def on_ready():
    print(f"Logged in as {discord_client.user}")

@discord_client.event
async def on_message(message):
    if message.author.id == discord_client.user.id:
        return

    if isinstance(message.channel, discord.DMChannel) and message.author.id in WHITELISTED_USER_IDS:
        user_id = message.author.id
        prompt = message.content.strip()
        if user_id not in user_conversations:
            user_conversations[user_id] = [{"role": "system", "content": system_prompt}]
        user_conversations[user_id].append({"role": "user", "content": prompt})

        try:
            chat_completion = groq_client.chat.completions.create(
                messages=user_conversations[user_id],
                model=aimodel,
                stream=False,
                temperature=1
            )

            reply = re.sub(r'<think>.*?</think>', '', chat_completion.choices[0].message.content)
            user_conversations[user_id].append({"role": "assistant", "content": reply})
            for i in range(0, len(reply), 2000):
                if delay:
                    await asyncio.sleep(random.randint(1, 6))
                await message.channel.send(reply[i:i + 2000])

            print(f"Reply: {message.author} - Reply: {reply[:2000]}")
            logging.info(f"DM: {message.author} - Reply: {reply[:2000]}")

        except Exception as e:
            print(f"Error: {e}")

    if message.reference and message.reference.message_id == discord_client.user.id:
        prompt = message.content.strip()

        try:
            chat_completion = groq_client.chat.completions.create(
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                model=aimodel,
                stream=False,
                temperature=1
            )

            reply = re.sub(r'<think>.*?</think>', '', chat_completion.choices[0].message.content)
            await message.channel.send(reply[:2000])
            print(f"Reply: {message.author} - Reply: {reply[:2000]}")
            logging.info(f"Reply: {message.author} - Reply: {reply[:2000]}")

        except Exception as e:
            print(f"Error: {e}")

discord_client.run(TOKEN)
