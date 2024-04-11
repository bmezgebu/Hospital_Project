import json
import openai
import PyPDF2
import os
import concurrent.futures
import openai.error
import time
import random
from dotenv import load_dotenv

# API Setup
load_dotenv('/Users/bereketdaniel/Desktop/Research Project/local_run/Hospital_Project/notes.env')  
api_key = os.getenv("API_KEY")
openai.api_key = api_key

# Extract training material from PDF
pdf_path1 = 'Training_Info_Full_Length.pdf'

def pdf_extractor(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for i in range(len(reader.pages)):
            page = reader.pages[i]
            text += page.extract_text()
    return text

trainingMaterials = pdf_extractor(pdf_path1)

# Extract Sample Conversations from PDF - used to model synthetic conversations
pdf_path2 = 'sampleHCPtoPatientConversations.pdf'
sampleConversations = pdf_extractor(pdf_path2)

prompt1 = "The following data is guidelines and information on post-operative care instruction best practices. Analyze this in preparation for the next prompt. Do not respond to this information with a summary or analysis; just analyse and retain it in preparation for the next prompt:" + trainingMaterials

def generate_conversation(max_retries = 3):
    HCP = random.choice(HCP_list)
    patientRepresentative = random.choice(patientRepresentative_list)
    surgicalProcedure = random.choice(surgicalProcedure_list)
    knowledgeCheck = knowledgeCheckGenerator()
    tone = toneRandomizer()
    messages = [
        {"role": "system", "content": f"""You are a Health Care Professional (HCP) to Patient Representative (such as the patient's family member, friend, or spouse) conversation generator with the topic of conversation being post-operative care procedures for a patient. Your task is to generate a single one of conversation that is as long as possible, based on parameters, sample conversations, and other training material you will be given. Do not stop writing until it is impossible to continue."""},
        {"role": "user", "content": f"""Generate a single conversation between a Health Care Provider (HCP) and Patient Representative (such as the patient's family member, friend, or spouse) with the following specifications:
        HCP: The Health Care Professional in this conversation should be a {HCP}.
        Patient Representative: The Patient Representative in this conversation should be the patient's {patientRepresentative}.
        Surgical Procedure: The manner of expression in the conversation should be {surgicalProcedure}.
        Questions: As demonstrated in the sample conversations, after the PCP provides instructions, they may ask a few questions to check Patient Representative's of the instructions they are being given. In this conversation, {knowledgeCheck}. The PCP should ask the questions at the end of the conversation. 
        PCP: The Primary Care Physician should have a {tone} tone.
        Patient Representative: The patient representative should work with the PCP by taking instructions, answering questions, and being focused while the PCP provides post-operative care instructions. 
        Now generate the conversation, which should be as long as possible, starting with the PCP's first message which should include them introducing themselves and the purpose of the conversation in a format similar (but not identical) to this: 
        PCP: Hi there! My name is [PCP Name] and I am the nurse working with Dr. [Doctor Name]] today. I am going to go over some of the post op education for [surgical procedure] before you speak to the scheduler.
        Patient Representative: Ok"""}
    ]

    for attempt in range(max_retries):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0125-preview",
                messages=messages,
            )
            return {
                "parameters": {
                    "HCP": HCP,
                    "patientRepresentative": patientRepresentative,
                    "surgicalProcedure": surgicalProcedure,
                    "knowledgeCheck": knowledgeCheck,
                    "tone": tone
                },
                "conversation": response['choices'][0]['message']['content']
            }

        except openai.error.OpenAIError as e:
            print(f'OpenAI error occurred: {e}, attempt {attempt + 1} of {max_retries}')
            time.sleep(1)
        
    print(f'Failed after {max_retries} attempts')
    return None


def process_file(output_file):
    start_time = time.time()

    # Open the file in write mode initially to create the file or overwrite an existing one
    with open(output_file, 'w') as out_file:
        out_file.write('[')  # Start the JSON array

    with open(output_file, 'a') as out_file:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit 5 tasks to the executor
            futures = [executor.submit(generate_conversation) for _ in range(5)]
            results = []

            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                try:
                    data = future.result()
                    results.append(data)
                except Exception as exc:
                    print('Generated an exception: %s' % exc)

            # Write results to the file, handling commas correctly
            for i, data in enumerate(results):
                json_data = json.dumps(data)
                if i != 0:  # Add a comma before each object except the first
                    out_file.write(',')
                out_file.write(json_data)

        out_file.write(']')  # Close the JSON array

    end_time = time.time()
    print("Time taken: {} seconds".format(end_time - start_time))


HCP_list = ["Doctor", "Nurse"]

patientRepresentative_list = ["Parent", "Spouse", "Sibling", "Friend"]

surgicalProcedure_list = ["Cataract Surgery", "Arthroscopic Surgery", "Tonsillectomy", "Hernia Repair", "Gallbladder Removal", "Carpal Tunnel Release", "Laser Eye Surgery", "Varicose Vein Treatment", "Endoscopic Sinus Surgery", "Skin Lesion Removals", "Breast Biopsy", "Ear Tube Placement", "Laparoscopic Sterilization", "Wisdom Teeth Extraction", "Appendectomy"]

# Randomly decide how many questions the PCP asks, how many of those questions the patient representative answers correctly, and whether the PCP reponds appropriately
def knowledgeCheckGenerator():
    numQuestions = random.choice([1,2,3])
    if numQuestions == 1:
        return "the PCP asks one question. The Patient Representative answers the question correctly."
    elif numQuestions == 2:
        return "the PCP asks two questions. The Patient Representative answers the first question incorrectly, then answers the second question correctly."
    else:
        return "the PCP asks three question. The Patient Representative answers the first two question incorrectly, then answers the third question correctly."
    
# Choose the tone of the HCP. 
# 0.6 probability of a 'professional, empathetic, informative' tone. 
# 0.3 probability of a 'semi-professional, neutral' tone. 
# 0.1 probability of a 'unprofessional, somewhat disrespectful, rushed' tone.
def toneRandomizer():
    tones = ['professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'semi-professional, neutral', 'semi-professional, neutral', 'semi-professional, neutral','unprofessional, somewhat disrespectful, rushed']
    return random.choice(tones)

output_file_path = '/Users/bereketdaniel/Desktop/Research Project/local_run/conversationGenerationInitialTesting/test2.json'

process_file(output_file_path)