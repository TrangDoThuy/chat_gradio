import openai
import time
import os

import gradio as gr

from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")

LAST_CALL_TIME = 0

messages = [
    {"role": "system", "content": """You are ChatBot, an empathetic assistant of professional mental coach in a mental coaching session. 
    You will talk with client  who is seeking mental help.
    
    Then please ask client 5 empathy curious deep open-ended questions to get more specific information as much as possible about the problem of client to find out the cause of problem.
    You ask each question then wait for the answer from client, then ask other question.
    The number of questions is limited to 5
    Please to not provide any advice or suggestion or guidance to client.
    If they ask what should they do or ask for any suggestion aor guidance, please say that: "We're matching you with a coach based on your unique situation to provide personalized guidance and support."
    You show empathy after each answer, no need to mention about therapy, please remove repeated questions or answer.
    The purpose of this conversation is to gather client information so that the real therapist can provide suggestion, 
    the conversation start from you saying thanks for coming and ask what brings them to counseling.
    Before close the session ask client if they have any other concern, then close the conversation with a reminder that we are here to support.
    Finish with "We're matching you with a coach based on your unique situation to provide personalized guidance and support."
    """},
    {"role": "assistant", "content": "Welcome to Kossie! I'm Kaia. How are you feeling today?"}
]

def _check_rate_limit():
    global LAST_CALL_TIME
    current_time = time.time()
    duration = current_time - LAST_CALL_TIME
    if duration < 20:
        time.sleep(20 - duration + 5)
    LAST_CALL_TIME = current_time

def respond(input, message_pair):
    _check_rate_limit()
    messages.append({"role": "user", "content": input})
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    bot_message = chat.choices[0].message.content
    message_pair.append((input, bot_message))
    messages.append({"role": "assistant", "content": bot_message})
    string = "Input: "+ input + "\n" + "ChatBot: "+ bot_message + "\n"
    print(string)
    f = open("conversation.txt", "a")
    f.write(string)
    f.close()
    return "", message_pair

def summary():
    _check_rate_limit()
    prompt = f"""
    Your task is to generate a short summary about user mental issue from a conversation in a counselling session between user and assistant.

    Given the conversation below, please summarize the content of user, delimited by triple 
    backticks, in at most 250 words. 
    The summary should be written from client perspective, using subject as "I". Please do not mention about counselor or coach in the summary.
    End with a question that user want to ask the coach to solve his/her problem. 

    Conversation: ```{messages}```
    """
    summary_request = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=summary_request,
        temperature=0, # this is the degree of randomness of the model's output
    )
    summary = response.choices[0].message["content"]
    f = open("conversation.txt", "a")
    summary_string = "---Summary---" + "\n" + summary + "\n" + "-----------------------" + "\n"
    f.write(summary_string)
    f.close()
    return summary

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(value=[["","Welcome to Kossie! I'm Kaia. How are you feeling today?"]])
    msg = gr.Textbox()
    finished = gr.Button("Finish conversation")
    summary_box = gr.Textbox(label="Summary")

    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    finished.click(fn=summary, inputs=None, outputs=summary_box, queue=False)
    
shareable = True
demo.launch(share=shareable)

