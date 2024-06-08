import os
import boto3
import time
import speech_recognition as sr
from boto3.session import Session
# from playsound import playsound
from io import BytesIO
import requests
import json
import threading
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import asyncio
import wave
from pydub import AudioSegment
from os import path
from daily import Daily,CallClient
from pydub import AudioSegment
from dotenv import load_dotenv
import glob
load_dotenv()





session = Session(
    aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
    aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
    region_name=os.environ['AWS_REGION']
)
polly_client = session.client('polly')
transcribe = boto3.client('transcribe', region_name=os.environ['AWS_REGION'],
                          aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
                          aws_secret_access_key=os.environ['AWS_SECRET_KEY'])
recognizer = sr.Recognizer()
recognizer.energy_threshold = 2000


import getpass
import os


model = ChatOpenAI(model="gpt-4o")

prompt_template =   ''' 
                    You are an interviewer bot for the AI intern position. Talk like an actual human, like use hmm, okay, sure, right! so that i can pass it to TTS. ask the right questions and you can choose to ask 1. follow-up questions 2. completely new question
                    Cover basic questions
                    '''

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",prompt_template
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chain = prompt | model
config = {"configurable": {"session_id": "abc5"}}

def get_chatgpt_response(prompt):
    response = chain.invoke(
    [HumanMessage(content=prompt)],
    config=config,)
    return(response.content.replace('\n','...'))

async def aws_polly_speak(text):
    session = Session(
        aws_access_key_id=os.environ['AWS_ACCESS_KEY'],
        aws_secret_access_key=os.environ['AWS_SECRET_KEY'],
        region_name=os.environ['AWS_REGION']
    )
    polly_client = session.client('polly')
    try:
        synthesis_start_time = time.time() 
        response = polly_client.synthesize_speech(
            VoiceId='Matthew',
            OutputFormat='mp3',
            Engine='neural',#generative
            Text=text)
        audio_stream = BytesIO(response['AudioStream'].read())
        temp_audio_path = f"temp_audio{time.time()}.mp3"
        file_2 = temp_audio_path.replace('.mp3','.wav')
        with open(temp_audio_path, "wb") as file:
            file.write(audio_stream.getvalue())
        sound = AudioSegment.from_mp3(temp_audio_path)
        sound.export(file_2, format="wav")
        os.rename(file_2, "bot/"+file_2)

        #print(f"Time taken for speech synthesis: {synthesis_time:.2f} seconds")
        #print(f"Time taken for generating the temp file: {file_generation_time:.2f} seconds")
        # playsound(temp_audio_path)
        os.remove(temp_audio_path)
        
    except Exception as e:
        print(str(e))
        

        
        
async def process_stream(stream):
    current_sentence = ""
    for chunk in stream:
        content = chunk.content
        current_sentence += content
        if content.endswith(".") or content in ["\n",'.','?']:
            sentence_to_run = current_sentence.strip()
            await aws_polly_speak(sentence_to_run) 
            current_sentence = ""

async def main(stream):
    stream = chain.stream(stream)
    await process_stream(stream)
                
def start_transcribe_stream():
        #aws_polly_speak_start("Hello, I'm your AI interviewer. Let's chat!  Just listen when I talk, and keep your answers short and sweet.  To begin, why don't you tell us a bit about yourself?")


        while True:
            files = list(os.listdir("student"))
            files.remove(".gitkeep")
            if len(files) != 0:
                file = files[0]
                print("file: ", file)
                file_name = f"student/{file}"
                dest_file = f"student_temp/{file}"
                print(file_name)
                user_input = None
                try:
                    with sr.AudioFile(file_name) as source:

                        source = recognizer.record(source)
                        print("source: ", source)
                        os.rename(file_name, dest_file)
                        [os.remove(i) for i in glob.iglob("student/*.wav")]
                        try:
                            
                            user_input = recognizer.recognize_google(source)
                            print(user_input)
                            asyncio.run(main({"messages": [HumanMessage(content=user_input)]}))
                        except Exception as e:
                            print(e)
                except Exception as e:
                    print(e)
                    ''' 
                    user_input = recognizer.recognize_amazon(audio_data, bucket_name=None,
                                                            access_key_id=AWS_ACCESS_KEY,
                                                            secret_access_key=AWS_SECRET_KEY,
                                                            region=AWS_REGION,
                                                            job_name=None,
                                                            file_key=None)
                    '''

                    
                    if user_input is not None:
                        print("user_input: ", user_input)
                        asyncio.run(main({"messages": [HumanMessage(content=user_input)]}))
            else:
                pass    
                                    
if __name__ == "__main__":
    transcribe_thread = threading.Thread(target=start_transcribe_stream)
    transcribe_thread.start()
