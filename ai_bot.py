import json
import os
import time
import openai
import requests
from openai import OpenAI
from config import Config
from packaging import version
from outlook_wraper import OutlookWraper
from airtable_wrapper import Airtable
from flask import Flask, request, jsonify
import functions

required_version = version.parse("1.1.1")
current_version = version.parse(openai.__version__)

class ConversationManager:
    def __init__(self):
        if current_version < required_version:
            raise ValueError(
                f"Error: OpenAI version {openai.__version__} is less than the required version 1.1.1"
            )
        else:
            print("OpenAI version is compatible.")
        
        # Initialize OpenAI client    
        self.client =OpenAI(api_key=Config.OPENAI_API_KEY)
        
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        self.invoices_airtable = Airtable(Config.INVOICE_AIRTABLE_TOKEN, 
                                          Config.INVOICE_AIRTABLE_BASE_ID, 
                                          Config.INVOICE_AIRTABLE_TABLE_ID, 
                                          Config.INVOICE_AIRTABLE_FIELDS)
        self.invoices = self.invoices_airtable.get_all_records()
        
        
        self.inventory_airtable = Airtable(Config.INVENTORY_AIRTABLE_TOKEN, 
                                           Config.INVENTORY_AIRTABLE_BASE_ID, 
                                           Config.INVENTORY_AIRTABLE_TABLE_ID, 
                                           Config.INVENTORY_AIRTABLE_FIELDS)
        self.inventory = self.inventory_airtable.get_all_records()
        
        self.outlook_wraper = OutlookWraper()
        self.assistant_id = function
    
    # Start a conversation thread
    def start_conversation(self, platform="Not Specified"):
        print("Starting a conversation...")
        
        thread = self.client.beta.threads.create()
        print(f"new thread created with ID: {thread.id}")
        
        return jsonify({"thread_id": thread.id})
        
    def chat(self, thread_id, user_input):
        print(f"Received message: {user_input} for thread ID: {thread_id}")
        
        # Add the user's message to the thread
        self.client.beta.threads.messages.create(thread_id=thread_id,
                                                 role="user",
                                                 content=user_input)
        
        # Run the assistent
        run = self.client.beta.threads.runs.create(thread_id=thread_id,
                                                   assistant_id=self.assistant_id)
        # Check if assistant requires function call
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=thread_id,
                                                                run_id=run.id)
            if run_status.status == 'completed':
                break

            elif run_status.status == 'requires_action':
                tools_outputs = []

                # Handle the function call
                for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                    if tool_call.function.name == 'save_answers':
                        arguments = json.loads(tool_call.function.arguments)
                        output = functions.save_answers(**arguments)

                        tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})

                time.sleep(1)  # Wait for a second before checking again

                if run_status.required_action.type == 'submit_tool_outputs':
                    print("Submit output")
                    self.client.beta.threads.runs.submit_tool_outputs(thread_id=thread_id, run_id=run.id,
                                                                       tool_outputs=tools_outputs)

        # Retrieve and return the latest message from the assistant
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        response = messages.data[0].content[0].text.value

        print(f"Assistant response: {response}")
        return response           
    
if __name__ == '__main__':
    conversation_manager = ConversationManager()
    thread_id = conversation_manager.start_conversation()

    while True:
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break

        response = conversation_manager.chat(thread_id, user_input)
        print("Assistant:", response)
