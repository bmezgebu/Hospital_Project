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
load_dotenv('/Users/bereketdaniel/Desktop/Research/local_run/Hospital_Project/notes.env')  
api_key = os.getenv("API_KEY")
openai.api_key = api_key

# Extract training material from PDF
def pdf_extractor(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

trainingMaterials = pdf_extractor('HospitalProjectFeedbackTrainingMaterials.pdf')
sampleConversations = pdf_extractor('sampleHCPtoPatientConversations.pdf')

def generate_conversation(max_retries=3):
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
            # Generate the first conversation
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
            )
            conversation_part1 = response['choices'][0]['message']['content']

            # Feedback prompt
            feedbackPrompt = (
                f"Please provide a detailed critical analysis of the Health Care Professional's (HCP) performance in the following conversation, "
                f"especially in light of the five key communication principles outlined in the training materials. These principles are: "
                f"1) Be welcoming to foster a comfortable dialogue environment, "
                f"2) Avoid jargon to ensure clear communication, "
                f"3) Stick to main points to maintain focus, "
                f"4) Ask teach-back questions to confirm understanding, and "
                f"5) Act in a manner that encourages the patient's representative to ask questions. "
                f"Review the training materials provided and the conversation below, then critically assess how well the HCP adhered to these principles. Cite examples from the conversation as support for each piece of feedback."
                f"Highlight both strengths and areas for improvement. Use specific examples from the conversation to support your points. \n\n"
                f"Training Materials: {trainingMaterials}\n\n"
                f"Conversation: {conversation_part1}"
            )

            messages.append({"role": "user", "content": feedbackPrompt})

            # Continue the conversation
            response = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=messages,
            )
            conversation_part2 = response['choices'][0]['message']['content']

            return {
                "parameters": {
                    "HCP": HCP,
                    "patientRepresentative": patientRepresentative,
                    "surgicalProcedure": surgicalProcedure,
                    "knowledgeCheck": knowledgeCheck,
                    "tone": tone
                },
                "conversation_part1": conversation_part1,
                "conversation_part2": conversation_part2
            }

        except openai.error.OpenAIError as e:
            print(f'OpenAI error occurred: {e}, attempt {attempt + 1} of {max_retries}')
            time.sleep(1)
        
    print(f'Failed after {max_retries} attempts')
    return None

# Definitions for conversation generation
HCP_list = ["Doctor", "Nurse"]
patientRepresentative_list = ["Parent", "Spouse", "Sibling", "Friend"]
surgicalProcedure_list = ["Cataract Surgery", "Arthroscopic Surgery", "Tonsillectomy", "Hernia Repair", "Gallbladder Removal", "Carpal Tunnel Release", "Laser Eye Surgery", "Varicose Vein Treatment", "Endoscopic Sinus Surgery", "Skin Lesion Removals", "Breast Biopsy", "Ear Tube Placement", "Laparoscopic Sterilization", "Wisdom Teeth Extraction", "Appendectomy"]

def knowledgeCheckGenerator():
    numQuestions = random.choice([1, 2, 3])
    responses = {
        1: "the PCP asks one question, which is answered correctly by the Patient Representative.",
        2: "the PCP asks two questions; the first is answered incorrectly, the second correctly.",
        3: "the PCP asks three questions; the first two are answered incorrectly, the last correctly."
    }
    return responses[numQuestions]

def toneRandomizer():
    tones = ['professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'professional, empathetic, informative', 'semi-professional, neutral', 'semi-professional, neutral', 'semi-professional, neutral','unprofessional, somewhat disrespectful, rushed']
    return random.choice(tones)

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

output_file_path = '/Users/bereketdaniel/Desktop/Research/local_run/conversationGenerationInitialTesting/test3.json'
process_file(output_file_path)

