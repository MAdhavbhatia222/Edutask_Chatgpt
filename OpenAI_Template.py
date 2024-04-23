import warnings
import os
import re
from unstructured_client import UnstructuredClient
from unstructured.partition.auto import partition
from unstructured.partition.pdf import partition_pdf
import chromadb
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
from langchain.chains.question_answering import load_qa_chain
from datetime import datetime, timedelta
import pandas as pd
from datetime import datetime, timedelta

# Suppress warnings
warnings.filterwarnings('ignore')

# Assuming the existence of a Utils class for API keys
from Utils import Utils

def get_current_week_dates_with_year(n_days=6):
    # Calculate the current date and the date six days later
    current_date = datetime.now()
    end_date = current_date + timedelta(days=n_days)

    # Format the start date as "Month day" and the end date as "day, Year"
    # Also, extract the current year
    start_date_formatted = current_date.strftime("%B %d")
    end_date_formatted = end_date.strftime("%B %d")
    current_year = current_date.strftime("%Y")
    start_date_sample = current_date.strftime("%B/%d")
    end_date_sample = end_date.strftime("%B/%d")
    return start_date_formatted, end_date_formatted, current_year,start_date_sample,end_date_sample


def parse_output(text):
    # Use regex to capture the contents of each cell within the pipes
    # This pattern matches lines with five groups of characters, each group is between pipes
    rows = re.findall(r"\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|", text)
    
    if rows:
        # Create DataFrame from matched rows
        tasks_dataframe_parsed = pd.DataFrame(rows, columns=["Date", "Task", "Effort Level", "Estimated Time", "Subject Name"])
        
        # Filter out any header or separator rows that might have been captured
        tasks_dataframe_filtered = tasks_dataframe_parsed[~tasks_dataframe_parsed['Date'].isin(["Date", "---", ""])]
        
        # Further filter tasks to remove any entries with placeholders or missing task names
        tasks_dataframe_filtered = tasks_dataframe_filtered[~tasks_dataframe_filtered['Task'].isin(["---", "", "NaN"])]
        
        # Return the cleaned DataFrame without sorting by 'Date' as it's treated as text
        return tasks_dataframe_filtered
    else:
        return pd.DataFrame()

class SyllabusProcessor:
    def __init__(self, dlai_api_key, dlai_api_url, openai_api_key_file_path, db_path="db"):
        self.dlai_client = UnstructuredClient(api_key_auth=dlai_api_key, server_url=dlai_api_url)
        self.db_client = chromadb.PersistentClient(path=db_path, settings=chromadb.Settings(allow_reset=True))
        self.openai_api_key = self.load_openai_api_key(openai_api_key_file_path)
        self.clear_database()  # Clear the database immediately upon initialization
        if self.openai_api_key is not None:
            self.llm = ChatOpenAI(openai_api_key=self.openai_api_key, temperature=0, model_name="gpt-3.5-turbo-1106")
        else:
            raise ValueError("OpenAI API Key could not be loaded.")

    @staticmethod
    def load_openai_api_key(file_path):
        try:
            with open(file_path, 'r') as file:
                return file.read().strip()  # .strip() to remove any trailing newline or spaces
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
            return None
        except Exception as e:
            print(f"An error occurred: {e}")
            return None
    
    def sanitize_collection_name(self, name):
        """
        Sanitizes the collection name to conform to chromadb requirements:
        - Contains 3-63 characters
        - Starts and ends with an alphanumeric character
        - Contains only alphanumeric characters, underscores, or hyphens
        - Contains no two consecutive periods (..)
        - Is not a valid IPv4 address
        """
        # Remove spaces and replace with underscores
        name = name.replace(" ", "_").replace(".docx", "").replace(".pdf", "").replace(".png", "")
        
        # Ensure the name starts and ends with alphanumeric characters
        name = re.sub(r'^[^a-zA-Z0-9]+|[^a-zA-Z0-9]+$', '', name)
        
        # Replace any sequence of non-alphanumeric characters with a single underscore
        name = re.sub(r'[^a-zA-Z0-9]+', '_', name)
        
        # Trim the name to 63 characters if necessary
        name = name[:63]  # Adjust based on max length to leave room for timestamp
        return name
    
    def clear_database(self):
        """
        Clears the database to ensure no existing collections conflict with new ones.
        WARNING: This operation will remove all data. Use with caution.
        """
        try:
            # Assuming `reset` is the method to clear the database, as per your earlier message.
            # Adjust this according to the actual capabilities of `chromadb`.
            self.db_client.reset()
            # print("Database cleared successfully.")
        except Exception as e:
            print(f"Error clearing the database: {e}")

    
    def get_collection_name_from_filename(self, filename):
        """Generate the sanitized collection name based on the filename."""
        base_name = os.path.basename(filename)
        sanitized_name = self.sanitize_collection_name(base_name)
        collection_name = "syllabus_" + sanitized_name
        return collection_name

    def process_document(self, filepath):
        # print("filepath_process_document",filepath)
        try:
            elements = partition(filename=filepath, strategy='fast')
        except:
            elements = partition_pdf(filename=filepath)

        original_name = os.path.basename(filepath).split('.')[0]
        collection_name = "syllabus_" + self.sanitize_collection_name(original_name)
        try:
            collection = self.db_client.create_collection(name=collection_name, metadata={"hnsw:space": "cosine"})
        except:
            pass
        for element in elements:
            parent_id = element.metadata.parent_id
            chapter = "Syllabus_Detail" if parent_id else ""
            collection.add(documents=element.text, ids=element.id, metadatas=[{"chapter": chapter}])

        print(f"Processed and added documents from {filepath} to collection {collection_name}")
        return collection_name




    def perform_similarity_search(self, collection_name, query):
        """
        Perform a similarity search on the specified collection and return results.
        This function now returns the text of the first document in the query result,
        assuming this text is relevant for generating a task list.
        """
        collection = self.db_client.get_collection(collection_name)
        result = collection.query(query_texts=[query],n_results=100)  # Assuming we're interested in the top result
        if result["documents"]:
            # Extract and return the text of the first document
            return str(result["documents"][0])
        else:
            return "No relevant content found for this query."
    
    def process_and_query_all_documents(self, directory, query):
        df_initial = pd.DataFrame()  # Initialize an empty list to store all tasks
        for filename in os.listdir(directory):
            if filename.startswith('.'):
                continue
            filepath = os.path.join(directory, filename)
            self.process_document(filepath)
            
            collection_name = self.get_collection_name_from_filename(filepath)
            print(f"\nQuerying collection derived from: {os.path.basename(filepath)}")
            
            context = self.perform_similarity_search(collection_name, query)
            
            task_list = self.generate_task_list(context)
            if task_list:  # If the task list is not empty
                df_output = parse_output(task_list)
                # Append the task list to all_tasks
                df_initial = pd.concat([df_initial,df_output], ignore_index=True)
        return df_initial


    
    def generate_task_list(self, context):
        query_prompt = """
        Generate a comprehensive list of tasks from the syllabus. This list will be used to create a CSV file with pandas, so it's crucial that the format is precise and directly usable. For each task, include the following details:
    
        - Actionable Description: Specify exactly what needs to be done. Avoid vague or placeholder entries; each task should be clearly defined and directly related to the syllabus content.
        - Date: List the exact date when each task is due. In case the date is not known then extrapolate based on the course schedule, upcoming exams, and project deadlines to create actionable tasks for each day within the specified week. You will follow "dd/mm/yyyy" format.
        - Effort Level: Assign a 'Low', 'Medium', or 'High' effort level based on the task's complexity and the time required to complete it.
        - Estimated Completion Time: Provide a realistic time estimate for completing the task, considering someone with a beginner's level of expertise in the subject matter.
        - Subject Name: Specify the subject name from the context. Avoid vague or placeholder entries; Course name remains the same for all tasks.
        
        Format the output as plain text, structured for CSV compatibility, like this:
        | Date | Task | Effort Level | Estimated Time | Subject Name |
        | [date] | [task name] | [effort level] | [time in hours] | [subject name] |
        | [date] | [task name] | [effort level] | [time in hours] | [subject name] |
        
        Avoid using ||
        Strictly delimit using |
        Avoid using 'None', 'N/A', or any placeholders for tasks. 
        Focus on identifying and detailing actual assignments, readings, preparation for exams, or projects mentioned in the syllabus or inferred from it. Identify as many tasks as possible.
        If the syllabus does not specify tasks for a given date, extrapolate based on the course schedule, upcoming exams, and project deadlines to create actionable tasks for each day within the specified week.
        """
        
        prompt = PromptTemplate(
        input_variables=["context", "query"],
        template="""
        Use the following pieces of context to answer the question at the end. If you 
        don't know the answer, just say that you don't know, don't try to make up an 
        answer.

        {context}

        Question: {query}
        Helpful Answer:
        """
        )

        chain = load_qa_chain(self.llm, chain_type="stuff", prompt=prompt, document_variable_name="context")
        response = chain.invoke(input={"input_documents": [Document(page_content=context)], "query": query_prompt})
        return response['output_text']

if __name__ == "__main__":
    utils = Utils()
    DLAI_API_KEY = utils.get_dlai_api_key()
    DLAI_API_URL = utils.get_dlai_url()
    OPENAI_API_KEY_FILE_PATH = r"desktop_openai.txt"
    start_date, end_date, current_year,sample_start,sample_end = get_current_week_dates_with_year(6)
    
    processor = SyllabusProcessor(DLAI_API_KEY, DLAI_API_URL, OPENAI_API_KEY_FILE_PATH)
    SOURCE_DOCUMENTS_FOLDER = "source_documents"
    
    # Now explicitly calling the method to process documents and generate tasks
    query = "What are the dates and related content to that? Is there are any tasks or due items? Is there a subject name?"  # Example query
    all_tasks = processor.process_and_query_all_documents(SOURCE_DOCUMENTS_FOLDER, query)
    print("###############################")
    # Parse the outputs
    df_output_csv_string = all_tasks.to_csv(index=False)  # Keep header for clarity
    print(df_output_csv_string)  # This will be captured by your Flask app
    
