from gdoc_requests import change_doc_title
import requests
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

# Add YOUR chromedriver path here
chromedriver_path = "chromedriver"

# Add your Google Docs here
# Make sure permissions are set such that anyone can edit them
# Multiple docs will allow for parallelization
all_google_docs = ['https://docs.google.com/document/d/1HtdDW0Z2HPRe8wnJnxfz5gnKoLeo88c5wNB8V1SMM/edit',
                    'https://docs.google.com/document/d/1UjPImPdiLHP_mwvFkdmjEp43zqenqbFytdF9QGIs/edit',
                    'https://docs.google.com/document/d/1lLJV_P3iXDY9ccM9-Oejkdk22RFSRzHTb0JIBf1cQEoA/edit'
                    ]



def release_gdoc_locks():
    # Loading Driver 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(chromedriver_path,options=chrome_options)
    doc_freed = False
    for i in range(len(all_google_docs)):
            curr_link = all_google_docs[i]
            curr_doc_id = curr_link.split('/')[5]
            driver.get(curr_link)
            doc_title = driver.title
            if 'Currently_Busy' in doc_title:
                # Release lock
                success = change_doc_title(curr_doc_id, "Currently_Free")
                if(success == 200):
                    doc_freed = True
                    print("Released lock for the current doc")
                else:
                    print("Unable to release lock...")
            else:
                print("Doc Already Free")

    return

release_gdoc_locks()