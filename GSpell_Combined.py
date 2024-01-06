from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
from GSpell.Metrics import true_wer, semantic_score, edit_distance
import googleapiclient.discovery as discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCOPES = ['https://www.googleapis.com/auth/drive', "https://www.googleapis.com/auth/documents"]
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'


# Add your content and credentials path here
token_path = "token_content.json"
creds_path = "credentials.json"

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage(token_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(creds_path, SCOPES)
        credentials = tools.run_flow(flow, store)
    return credentials

def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')
    if not text_run:
        return ''
    return text_run.get('content')

def read_structural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """
    text = ''
    for value in elements:
        if 'paragraph' in value:
            elements = value.get('paragraph').get('elements')
            for elem in elements:
                text += read_paragraph_element(elem)
        elif 'table' in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get('table')
            for row in table.get('tableRows'):
                cells = row.get('tableCells')
                for cell in cells:
                    text += read_structural_elements(cell.get('content'))
        elif 'tableOfContents' in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get('tableOfContents')
            text += read_structural_elements(toc.get('content'))
    return text


credentials = get_credentials()
http = credentials.authorize(Http())
docs_service = discovery.build('docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)

def erase_text(driver):
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).send_keys('a').perform()
    webdriver.ActionChains(driver).key_up(Keys.CONTROL).key_down(Keys.BACKSPACE).perform()
    webdriver.ActionChains(driver).key_up(Keys.BACKSPACE).perform()
    time.sleep(0.01)

def send_text(driver,content):
    webdriver.ActionChains(driver).send_keys(content).perform()
    
def spell_check(driver):
    for i in range(1):
        for k in range(90): 
            time.sleep(0.1)   
            try:                
                webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.LEFT_ALT).send_keys('x').perform()
                webdriver.ActionChains(driver).key_up(Keys.CONTROL).key_up(Keys.LEFT_ALT).perform()
                
                element = driver.find_element("xpath", "//div[@class='docs-checkupdialog-button-change docs-checkupdialog-buttons-action docs-material-button-fill-primary docs-material-button']")
                
                webdriver.ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
            except:
                    webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.LEFT_ALT).send_keys('x').perform()
                    webdriver.ActionChains(driver).key_up(Keys.CONTROL).key_up(Keys.LEFT_ALT).perform()
                    webdriver.ActionChains(driver).key_down(Keys.TAB).key_up(Keys.TAB).perform()                    
                    webdriver.ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

def page_down(driver):
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ARROW_DOWN).key_up(Keys.CONTROL).key_up(Keys.ARROW_DOWN).perform()
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ARROW_DOWN).key_up(Keys.CONTROL).key_up(Keys.ARROW_DOWN).perform()    
    #time.sleep(0.1)

def page_top(driver):
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ARROW_UP).key_up(Keys.CONTROL).key_up(Keys.ARROW_UP).perform()
    webdriver.ActionChains(driver).key_down(Keys.CONTROL).key_down(Keys.ARROW_UP).key_up(Keys.CONTROL).key_up(Keys.ARROW_UP).perform()    
    time.sleep(0.1)    

def line_sep(driver):
    webdriver.ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
    webdriver.ActionChains(driver).key_down(Keys.ARROW_DOWN).key_up(Keys.ARROW_DOWN).perform()
    
def hit_enter(driver):
    webdriver.ActionChains(driver).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()

def send_escape(driver):
    webdriver.ActionChains(driver).key_down(Keys.ESCAPE).key_up(Keys.ESCAPE).perform()

def retrieve_gdocs_text(DOCUMENT_ID):
    all_content = []
    doc = docs_service.documents().get(documentId=DOCUMENT_ID).execute()
    doc_content = doc.get('body').get('content')
    temp_text = read_structural_elements(doc_content)
    all_content.append(temp_text)
    return ' '.join(all_content)

def get_text_with_periods(driver, doc_ID):

    content = retrieve_gdocs_text(doc_ID)
    content = content.encode("ascii", 'ignore')
    content = content.decode()
    content = content.replace("?", "")
    content = content.replace(".\n\n\n",". ")
    content = content.replace(",\n\n\n",". ")
    content = content.replace(", \n\n\n",". ")
    content = content.replace("\n\n\n",". ")
    content = content.replace(" \n\n\n",". ")
    content = content.replace(". \n\n\n",". ")
    content = content.replace(".\n\n", " ")
    content = content.replace(",\n\n", " ")
    content = content.replace("\n", " ")
    content = content.replace(u'\x03', u'')

    return content


def run_GSpell_aio_period(ground_truth, content, window_size, period_windows, driver, doc_ID):
    
    all_aio_metrics = {}
    content = content.replace("   ", " ").replace("  ", " ").replace(",.", ".").replace(".,", ".").replace(", ,", ",").replace("..", ".").replace(". .",".").replace(" .", ".").replace(" ,", ",").replace(". .", ".")
    content = content.replace(". ", ".").replace(", ", ",")
    content = content.replace(".", ". ").replace(",", ", ")

    for i in range(1):

        erase_text(driver)
        content_split = content.split(" ")
        tot_len = len(content_split)

        for idx, x in enumerate(window_size):

            metricss_curr_window = {}
            tot_len = len(content.split(' '))
            period_exists = False           
            for j in range(0,tot_len, x ):
                content_split = content.split(" ")
                curr_block = ' '.join(content_split[j:j+x]) 
                send_text(driver, curr_block)
                page_down(driver)
                hit_enter(driver)
                hit_enter(driver)
            
            
            spell_check(driver)
            time.sleep(2)
            spell_check(driver)
            time.sleep(2)
            spell_check(driver)
            time.sleep(2)
            spell_check(driver)
            time.sleep(2)
            spell_check(driver)
            time.sleep(2)
            send_escape(driver)    
            
            
            content = get_text_with_periods(driver, doc_ID)
            
            erase_text(driver)

            content_split = content.split(" ")
            content_split = [sent for sent in content_split if sent != ""]
            for k in range(1, len(content_split)):
                if content_split[k-1][-1] != ".":
                    content_split[k] = content_split[k].lower()

            
            content = ' '.join(content_split)
            content = content.replace("   ", " ").replace("  ", " ").replace(",.", ".").replace(".,", ".").replace(", ,", ",").replace("..", ".").replace(". .",".").replace(" .", ".").replace(" ,", ",").replace(". .", ".")
            content = content.replace(". ", ".").replace(", ", ",").replace(". .", ".")
            content = content.replace(".", ". ").replace(",", ", ").replace(" \t", "").replace("\t", "")
            
            
            # Compute stats and append to main metrics_dict        
            semantic_score_aio = semantic_score(content)
            wer_aio = true_wer(ground_truth, content)
            edit_distance_aio = edit_distance(ground_truth, content)

            # End computing stats
            # Saving results     

            aio_metrics = {}

            aio_metrics['Semantic_Score'] = semantic_score_aio
            aio_metrics['WER'] = wer_aio
            aio_metrics['Edit_Distance'] = edit_distance_aio
            aio_metrics['Gspell'] = content

            all_aio_metrics[f"Window_{idx}_{x}"] = aio_metrics

    content_split = content.split(" ")
    content_split = [sent for sent in content_split if sent != ""]
    for k in range(1, len(content_split)):
        if content_split[k-1][-1] != ".":
            content_split[k] = content_split[k].lower()

    content = ' '.join(content_split)

    content = content.replace("   ", " ").replace("  ", " ").replace(",.", ".").replace(".,", ".").replace(", ,", ",").replace("..", ".").replace(". .",".").replace(" .", ".").replace(" ,", ",").replace(". .", ".")
    content = content.replace(". ", ".").replace(", ", ",").replace(". .", ".")
    content = content.replace(".", ". ").replace(",", ", ")

    idx = len(window_size) - 1
    x = window_size[-1]
    all_aio_metrics['final_metrics'] = all_aio_metrics[f"Window_{idx}_{x}"]
    
    return all_aio_metrics, content