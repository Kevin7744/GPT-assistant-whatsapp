import json
import time
import openai
from openai import OpenAI
from config import Config
from packaging import version
import functions
import os

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
        
        self.thread_id = None
        self.load_thread_id()
        
        self.assistant_id = functions.create_assistant(self.client)
        if not self.thread_id:
            self.start_conversation()
            
    # load an initial thread id       
    def load_thread_id(self):
        if os.path.exists('thread_id.json'):
            with open('thread_id.json', 'r') as f:
                data = json.load(f)
                self.thread_id = data.get('thread_id')
                print(f"Loaded thread ID: {self.thread_id}")

    # save a thead_id when a new conversation is started
    def save_thread_id(self):
        with open('thread_id.json', 'w') as f:
            data = {'thread_id': self.thread_id}
            json.dump(data, f)
    
    # Start a conversation thread
    def start_conversation(self, platform="Not Specified"):
        print("Starting a conversation...")
        thread = self.client.beta.threads.create()
        print(f"new thread created with ID: {thread.id}")
        self.thread_id = thread.id
        self.save_thread_id()
        return self.thread_id
        
    def chat(self, user_input):
        if self.thread_id is None:
            raise ValueError("Thread ID is not set. Call start_conversation first.")
        
        print(f"Received message: {user_input} for thread ID: {self.thread_id}")
        
        # Add the user's message to the thread
        self.client.beta.threads.messages.create(thread_id=self.thread_id,
                                                role="user",
                                                content=user_input)
        
        # Run the assistant
        run = self.client.beta.threads.runs.create(thread_id=self.thread_id,
                                                assistant_id=self.assistant_id)
        
        # Check if assistant requires function call
        while True:
            run_status = self.client.beta.threads.runs.retrieve(thread_id=self.thread_id,
                                                                run_id=run.id)
            if run_status.status == 'completed':
                break
            
            elif run_status.status == 'requires_action':
                tools_outputs = []
                
                # Handle the function call
                if run_status.required_action and run_status.required_action.type == 'submit_tool_outputs':
                    for tool_call in run_status.required_action.submit_tool_outputs.tool_calls:
                        ###################################################################################################
                        # Handle function calling related to cleaning questions and save answers
                        if tool_call.function.name == "create_lead":
                            # Process lead creation
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.create_lead(arguments["name"], arguments["phone"],
                                                        arguments["address"], arguments["email"])
                            
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                        
                        elif tool_call.function.name == 'save_answers':
                            arguments = json.loads(tool_call.function.arguments)
                            print(arguments)
                            
                            output = functions.save_answers(
                                arguments.get('full_name', ''), 
                                arguments.get('phone', ''), 
                                arguments.get('email', ''), 
                                arguments.get('street_name', ''), 
                                arguments.get('zip_code', ''), 
                                arguments.get('city', ''), 
                                arguments.get('service_type', ''), 
                                arguments.get('ot1', ''),
                                arguments.get('ot2', ''), 
                                arguments.get('ot3', ''), 
                                arguments.get('ot4', ''),
                                arguments.get('ot5', ''), 
                                arguments.get('rc1', ''), 
                                arguments.get('rc2', ''), 
                                arguments.get('rc3', ''), 
                                arguments.get('rc4', ''), 
                                arguments.get('rc5', ''), 
                                arguments.get('pc1', ''),
                                arguments.get('pc2', ''),  
                                arguments.get('pc3', ''),  
                                arguments.get('pc4', ''),  
                                arguments.get('pc5', ''),  
                                arguments.get('pc6', ''),  
                                arguments.get('ww1', ''),  
                                arguments.get('ww2', ''),  
                                arguments.get('ww3', ''),  
                                arguments.get('ww4', ''), 
                                arguments.get('ww5', ''),  
                                arguments.get('cc1', ''), 
                                arguments.get('cc2', ''),  
                                arguments.get('cc3', ''),  
                                arguments.get('cc4', ''),  
                                arguments.get('sc1', ''), 
                                arguments.get('sc2', ''),  
                                arguments.get('sc3', ''),  
                                arguments.get('sc4', '') 
                            )
        
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                        
                        ####################################################################################################    
                        # Handles Function calling related to invoices
                        elif tool_call.function.name == "check_invoices":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.check_invoices()
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "create_invoice":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.create_invoice(arguments["business_name"], arguments["phone_number"], arguments["email"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "delete_invoice":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.delete_invoice(arguments["business_name"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "send_invoice":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.send_invoice(arguments["business_name"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                        
                        ######################################################################################################
                        # Handles function calling related to inventory
                        elif tool_call.function.name == "check_inventory":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.check_invoices()
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "change_inventory":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.change_inventory(arguments["product"], arguments["current_stock"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "create_inventory":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.create_inventory(arguments["product"], arguments["current_stock"], arguments["min_stock"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                        
                        ######################################################################################################
                        # Handles function calling related to calendar
                        elif tool_call.function.name == "current_date_time":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.current_date_time()
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "create_event":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.create_event(arguments["name"], arguments["date"], arguments["time"], arguments["duration"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})
                            
                        elif tool_call.function.name == "create_recurring_event":
                            arguments = json.loads(tool_call.function.arguments)
                            output = functions.create_recurring_event(arguments["name"], arguments["days_of_week"], arguments["start_time"], arguments["end_time"], arguments["start_date"], arguments["end_date"], arguments["length_weeks"])
                            tools_outputs.append({"tool_call_id": tool_call.id, "output": json.dumps(output)})            
                        
                time.sleep(2)  # Wait for a second before checking again
                
                if tools_outputs:
                    self.client.beta.threads.runs.submit_tool_outputs(thread_id=self.thread_id, run_id=run.id,
                                                                    tool_outputs=tools_outputs)
        
        # Retrieve and return the latest message from the assistant
        messages = self.client.beta.threads.messages.list(thread_id=self.thread_id)
        response = messages.data[0].content[0].text.value
        
        print(f"Assistant response: {response}")
        return response
    
    def handle_message(self, user_input):
        if self.thread_id is None:
            self.start_conversation()
        
        response = self.chat(user_input)
        return response
         
    
if __name__ == '__main__':
    bot = ConversationManager()

    while True:
        msg = input('User: ')
        print(f'BOT: {bot.handle_message(msg)}')