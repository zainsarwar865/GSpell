from pydoc import doc
from GSpell_Combined import run_GSpell_aio_period
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from gdoc_requests import change_doc_title

# Add YOUR chromedriver path here
chromedriver_path = "/home/zsarwar/chromedriver/chromedriver"
# Add your Google Docs here
# Make sure permissions are set such that anyone can edit them
# Multiple docs will allow for parallelization
all_google_docs = ['https://docs.google.com/document/d/1Kol0Z2HPRe8wnJnxfz5gToado9ByCMc5sdds1SMM/edit',
                    'https://docs.google.com/document/d/1udPdPImPdiLHP_mwvzddRg8f3ybIkzqenqbdsdsdF9QGIs/edit',
                    'https://docs.google.com/document/d/1lLJV_P3iXXhyPoM9-oaE2pmrRFSRzHTb0JIdsdsd1cQEoA/edit',
                    ]

def Run_GSpell_Metrics(ground_truth, predicted_text, period_windows, window_sizes, copyleaks_on=False):
    # Loading ChromeDriver 
    chrome_options = Options()
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--disable-crash-reporter')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=chromedriver_path,options=chrome_options)

    # Choose a Google doc not currently being used
    found_free_doc = False
    for i in range(len(all_google_docs)):
        curr_link = all_google_docs[i]
        curr_doc_id = curr_link.split('/')[5]
        driver.get(curr_link)
        doc_title = driver.title
        if 'Currently_Busy' not in doc_title:
            # Acquire lock for this doc
            print("Found free doc")
            success = change_doc_title(curr_doc_id, "Currently_Busy")
            if(success):
                found_free_doc = True
                print("Locked current doc")
                break
        else:
            print("This doc is busy, trying another one...")
    if(found_free_doc == False):
        print("No free Google docs available. Try later.")
        return 
    time.sleep(2)
    aio_metrics, gspell_text = run_GSpell_aio_period(ground_truth, predicted_text, window_sizes, period_windows, driver, curr_doc_id)
    # Release lock for Google Doc
    doc_freed = change_doc_title(curr_doc_id, "Currently_Free")
    if(doc_freed):
        print("Doc released")
    else:
        time.sleep(5)
        doc_freed = change_doc_title(curr_doc_id, "Currently_Free")
        if(doc_freed):
            print("Doc released")
        else:
            print("Doc not released - Manually change to Currently_Free")
            print(curr_link)
    return aio_metrics, gspell_text