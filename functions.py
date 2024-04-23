import json
import requests
import os
from openai import OpenAI
from prompts import assistant_instructions
from config import Config
from airtable_wrapper import Airtable
from outlook_wraper import OutlookWraper

# Init OpenAI Client
client = OpenAI(api_key=Config.OPENAI_API_KEY)



#############################-- Functions Related to invoices -- ##############################################
invoices_airtable = Airtable(Config.INVOICE_AIRTABLE_TOKEN, 
                            Config.INVOICE_AIRTABLE_BASE_ID, 
                            Config.INVOICE_AIRTABLE_TABLE_ID, 
                            Config.INVOICE_AIRTABLE_FIELDS)

# Function to get all invoice records
def check_invoices():
    """Function to get all the invoices records
    """
    return invoices_airtable.get_all_records()

# Function to create an invoice
def create_invoice(business_name, phone_number, email):
    """Function to create a new invoice

    Args:
        business_name (str): The name of the business
        phone_number (str, optional): The phone number of the business. Defaults to ''.
        email (str, optional): The email of the business. Defaults to ''.
        
    Returns:
        str: The response from the bot
    """
    output = {'Bedrijf': business_name}
            
    if phone_number:
        output['Telefoonnummer'] = phone_number
    
    if email:
        output['Email'] = email
    
    invoices_airtable.create_record(output)
    return f'Ok, I just created a new invoice for {business_name}. Is there anything else I can help you with?'


# Function to delete an invoice
def delete_invoice(business_name):
    """Function to delete an invoice

    Args:
        business_name (str): The name of the business
        
    Returns:
        str: The response from the bot
    """
    invoices_airtable.delete_record({'Bedrijf': business_name})
    return f'Ok, I just deleted an invoice for {business_name}. Do you need help with anything else?'


# Function to send an invoice
def send_invoice(business_name):
    """Function to send an invoice

    Args:
        business_name (str): The name of the business
        
    Returns:
        str: The response from the bot
    """
    if invoices_airtable.update_record({'Bedrijf': business_name.strip().title()}, {'Status Factuur': 'Factuur Versturen...'}):
        return f'Ok, I just updated the invoice status for {business_name}'



############################################# -- Functions related to Inventory -- ####################################################################
inventory_airtable = Airtable(Config.INVENTORY_AIRTABLE_TOKEN, 
                              Config.INVENTORY_AIRTABLE_BASE_ID, 
                              Config.INVENTORY_AIRTABLE_TABLE_ID, 
                              Config.INVENTORY_AIRTABLE_FIELDS)

        
# Function to get ll inventory records
def check_inventory():
    """Function to get all the inventory records
    """
    return inventory_airtable.get_all_records()

# Function to handle changes in inventory
def change_inventory(product, current_stock):
    """Function to update the stock of a product in inventory

    Args:
        product (str): The name of the product
        current_stock (int): The new current stock value
        
    Returns:
        str: The response from the bot
    """
    if inventory_airtable.update_record({'product': product}, {'huidige_stock': current_stock}):
        return f'Ok, I just updated the entry for {product}'
    else:
        return 'What you are trying to do is not possible. It is likely you entered the name of a product that does not exist.'

# Function to handle creating a new entry in inventory
def create_inventory(product, current_stock, min_stock):
    """Function to create a new entry in inventory

    Args:
        product (str): The name of the product
        current_stock (int): The current stock of the product
        min_stock (int): The minimum stock of the product
        
    Returns:
        str: The response from the bot
    """
    if inventory_airtable.create_record({'product': product, 'huidige_stock': current_stock, 'minimum_stock': min_stock}):
        return f'Ok, I just added an entry for a new product called {product}'
    else:
        return 'Unfortunately, there was an error processing your request. Please try again'
   


################################## -- Functions related to cleaning questions -- ###############################################################
def create_lead(name, phone, address, email):
    # Change this to your Airtable API URL
    url = "https://api.airtable.com/v0/appCkbD804q1OaxGh/Leads"
    headers = {
        "Authorization": Config.AIRTABLE_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "records": [{
            "fields": {
                "Name": name,
                "Phone": phone,
                "Address": address,
                "Email": email
            }
        }]
    }
    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        print("Lead created successfully.")
        return response.json()
    else:
        print(f"Failed to create lead: {response.text}")
        return ''

def save_answers(full_name, phone, email, street_name, zip_code, city,
                 service_type, 
                 ot1, ot2, ot3, ot4, ot5,  # responses for one-time cleaning
                 rc1, rc2, rc3, rc4, rc5,  # responses for regular cleaning
                 pc1, pc2, pc3, pc4, pc5, pc6,  # responses for post-construction cleaning
                 ww1, ww2, ww3, ww4, ww5,  # responses for window washing
                 cc1, cc2, cc3, cc4,  # responses for carpet cleaning
                 sc1, sc2, sc3, sc4  # responses for sofa cleaning
                 ):

    resp = requests.get(Config.MAKE_URL, data={
        'full_name': full_name,
        'street_name': street_name,
        'zip_code': zip_code,
        'phone': phone,
        'email': email,
        'city': city,
        'service_type': service_type, 
        'ot1': ot1,
        'ot2': ot2,
        'ot3': ot3,
        'ot4': ot4,
        'ot5': ot5,
        'rc1': rc1,
        'rc2': rc2,
        'rc3': rc3,
        'rc4': rc4,
        'rc5': rc5,
        'pc1': pc1,
        'pc2': pc2,
        'pc3': pc3,
        'pc4': pc4,
        'pc5': pc5,
        'pc6': pc6,
        'ww1': ww1,
        'ww2': ww2,
        'ww3': ww3,
        'ww4': ww4,
        'ww5': ww5,
        'cc1': cc1,
        'cc2': cc2,
        'cc3': cc3,
        'cc4': cc4,
        'sc1': sc1,
        'sc2': sc2,
        'sc3': sc3,
        'sc4': sc4
    })

    if resp.ok:
        print('Saved answers successfully')
        return resp.text
    else:
        print('Failed to save responses')
        return ''
    
    
#######################################################################################################
def create_assistant(client):
    assistant_file_path = 'assistant.json'
    
    # If there is an assistant.json file alreadt, then load that assistant
    if os.path.exists(assistant_file_path):
        with open(assistant_file_path, 'r') as file:
            assistant_data = json.load(file)
            assistant_id = assistant_data['assistant_id']
            print("Loaded existing assistant ID.")
    else: 
        # If no assistant.json is present, create a new assistant using
        file = client.files.create(file=open("knowledge.docx", "rb"), purpose='assistants')
        file_invoices = client.files.create(file=open("invoices.md", "rb"), purpose='assistants')
        file_inventory = client.files.create(file=open("inventory.md", "rb"), purpose='assistants')
        file_site_data = client.files.create(file=open('site_data.txt', 'rb'), purpose='assistants')

        assistant = client.beta.assistants.create(
            # Getting assistant prompt from "prompts.py" file, edit on left panel if you want to change the prompt
            instructions=assistant_instructions,
            model="gpt-4-1106-preview",
            tools=[
                {"type": "retrieval"},  # This adds the knowledge base as a tool
                {
                    "type": "function",
                    "function": {
                        "name": "check_invoices",  # This adds the check invoices function as a tool
                        "description": "Function to get all the existing invoices records",
                        "parameters": {}
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_invoice",  # This adds the create invoices function as a tool
                        "description": "Function to create a new invoice",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "business_name": {
                                    "type": "string",
                                    "description": "The name of the business"
                                },
                                "phone_number": {
                                    "type": "string",
                                    "description": "The phone number of the business"
                                },
                                "email": {
                                    "type": "string",
                                    "description": "The email of the business"
                                }
                            },
                            "required": ["business_name"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_invoice", # This adds the delete invoices function as a tool
                        "description": "Function to delete an invoice",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "business_name": {
                                    "type": "string",
                                    "description": "The name of the business"
                                }
                            },
                            "required": ["business_name"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "send_invoice", # This adds the send invoices function as a tool
                        "description": "Function to send an invoice",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "business_name": {
                                    "type": "string",
                                    "description": "The name of the business"
                                }
                            },
                            "required": ["business_name"]
                        }
                    }
                },
                {
                        "type": "function",
                        "function": {
                            "name": "check_inventory", # This adds the check_inventory function as a tool
                            "description": "Function to get all the inventory records"
                        }
                },
                {
                    "type": "function", 
                    "function": {
                        "name": "change_inventory", # This adds the change_inventory function as a tool
                        "description": "Function to update the stock of a product in inventory",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "product": {
                                    "type": "string",
                                    "description": "The name of the product"
                                },
                                "current_stock": {
                                    "type": "integer",
                                    "description": "The new current stock value"
                                }
                            },
                            "required": ["product", "current_stock"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "create_inventory", # This adds the create_inventory function as a tool
                        "description": "Function to create a new entry in inventory",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "product": {
                                    "type": "string",
                                    "description": "The name of the product"
                                },
                                "current_stock": {
                                    "type": "integer",
                                    "description": "The current stock of the product"
                                },
                                "min_stock": {
                                    "type": "integer",
                                    "description": "The minimum stock of the product"
                                }
                            },
                            "required": ["product", "current_stock", "min_stock"]
                        }
                    }
                },
                {
                    "type": "function",  # This adds the lead capture as a tool
                    "function": {
                        "name": "create_lead",
                        "description":
                        "Capture lead details and save to Airtable.",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Name of the lead."
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Phone number of the lead."
                                },
                                "address": {
                                    "type": "string",
                                    "description": "Address of the lead."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Email of the lead"
                                }
                            },
                            "required": ["name", "phone", "address", "email"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "save_answers", # This adds the save answers as a tool
                        "description": """Capture the details of the user and the answers provided by the user a cleaning service booking and send them to a designated endpoint. 
                                        You must collect the user's personal details (full_name, phone, email, street_name, zip_code, city) before submitting the data to the endpoint.""",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "full_name": {
                                    "type": "string",
                                    "description": "Full name of the user."
                                },
                                "phone": {
                                    "type": "string",
                                    "description": "Phone number of the user."
                                },
                                "email": {
                                    "type": "string",
                                    "description": "Email address of the user."
                                },
                                "street_name": {
                                    "type": "string",
                                    "description": "Street name of the user's address."
                                },
                                "zip_code": {
                                    "type": "string",
                                    "description": "Zip code of the user's location."
                                },
                                "city": {
                                    "type": "string",
                                    "description": "City of the user's residence."
                                },
                                "service_type": {
                                    "type": "string", 
                                    "description": "Type of cleaning service, one of: 'One-time cleaning', 'Regular cleaning', 'Post-construction cleaning', 'Window washing', 'Carpet Cleaning', 'Sofa Cleaning'"
                                }, 

                                "ot1": {"type": "string", "description": "Response for one-time cleaning question: 'Which standard cleaning tasks do you require? (required to have an answer)'"},
                                "ot2": {"type": "string", "description": "Response for one-time cleaning question: 'What is the total square footage (m²) of the space that needs to be cleaned? (required to have an answer)'"},
                                "ot3": {"type": "string", "description": "Response for one-time cleaning question: 'Are there specific spots or details that need extra attention?'"},
                                "ot4": {"type": "string", "description": "Response for one-time cleaning question: 'Are there specific cleaning products we should use, for instance, for a certain type of floor?'"},
                                "ot5": {"type": "string", "description": "Response for one-time cleaning question: 'Do you also wish the windows to be washed?'"},

                                "rc1": {"type": "string", "description": "Response for regular cleaning question 1: 'Desired cleaning frequency (required to have an answer)'"},
                                "rc2": {"type": "string", "description": "Response for regular cleaning question 2: 'How often per week do you want cleaning to be done? (required to have an answer)'"},
                                "rc3": {"type": "string", "description": "Response for regular cleaning question 3: 'What is the total square footage (m²) of the space that needs to be cleaned? (required to have an answer)'"},
                                "rc4": {"type": "string", "description": "Response for regular cleaning question 4: 'What standard cleaning tasks do you expect from us?'"},
                                "rc5": {"type": "string", "description": "Response for regular cleaning question 5: 'Are there specific focus points or additional tasks you want to be executed?'"},

                                "pc1": {"type": "string", "description": "Response for post-construction cleaning question 1: 'Which standard cleaning tasks do you require?'"},
                                "pc2": {"type": "string", "description": "Response for post-construction cleaning question 2: 'What is the current condition of the spaces?'"},
                                "pc3": {"type": "string", "description": "Response for post-construction cleaning question 3: 'Are there specific spots or details that need extra attention?'"},
                                "pc4": {"type": "string", "description": "Response for post-construction cleaning question 4: 'What is the total square footage (m²) of the space that needs to be cleaned? (required to have an answer)'"},
                                "pc5": {"type": "string", "description": "Response for post-construction cleaning question 5: 'Are there specific cleaning products we should use, for instance, for a certain type of floor?'"},
                                "pc6": {"type": "string", "description": "Response for post-construction cleaning question 6: 'Are there any traces of cement grout haze?'"},

                                "ww1": {"type": "string", "description": "Response for window washing question 1: 'What is the total square footage (m²) of the space that needs to be cleaned? (required to have an answer)'"},
                                "ww2": {"type": "string", "description": "Response for window washing question 2: 'How many windows approximately need to be washed?'"},
                                "ww3": {"type": "string", "description": "Response for window washing question 3: 'How dirty are the windows currently?'"},
                                "ww4": {"type": "string", "description": "Response for window washing question 4: 'Are they mostly large or small windows?'"},
                                "ww5": {"type": "string", "description": "Response for window washing question 5: 'Are there specific cleaning products we should use for the windows?'"},

                                "cc1": {"type": "string", "description": "Response for carpet cleaning question 1: 'What is the width of the carpet you want to be cleaned? (in meters) (required to have an answer)'"},
                                "cc2": {"type": "string", "description": "Response for carpet cleaning question 2: 'What is the length of the carpet you want to be cleaned? (in meters) (required to have an answer)'"},
                                "cc3": {"type": "string", "description": "Response for carpet cleaning question 3: 'If you wish to have multiple carpets cleaned, please specify the total number of carpets to be cleaned here.'"},
                                "cc4": {"type": "string", "description": "Response for carpet cleaning question 4: 'If you have multiple carpets with different dimensions that need cleaning, please specify the dimensions of each carpet here.'"},

                                "sc1": {"type": "string", "description": "Response for sofa cleaning question 1: 'How many sofas do you want to be cleaned? (required to have an answer)'"},
                                "sc2": {"type": "string", "description": "Response for sofa cleaning question 2: 'How many seating places do the sofa(s) you want to be cleaned have? (required to have an answer)'"},
                                "sc3": {"type": "string", "description": "Response for sofa cleaning question 3: 'If you have multiple sofas with different seating arrangements to be cleaned, please specify the details of each sofa here.'"},
                                "sc4": {"type": "string", "description": "Response for sofa cleaning question 4: 'Is it a corner sofa?'"}
                            },
                            "required": [
                                "full_name", "phone", "email", "street_name", "zip_code", "city"
                            ]
                        }
                    }
                }

            ],
            file_ids=[file.id, file_invoices.id, file_inventory.id, file_site_data.id])

        # Create a new assistant.json file to load on future runs
        with open(assistant_file_path, 'w') as file:
            json.dump({'assistant_id': assistant.id}, file)
            print("Created a new assistant and saved the ID.")

        assistant_id = assistant.id

    return assistant_id        

if __name__ == '__main__':
    save_answers('', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '')