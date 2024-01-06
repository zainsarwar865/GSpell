# GSpell
An API to access Google Doc's state of the art grammar / spell check 

This repository allows you to use the spelling and grammar checking tool which is provided by Google Docs. I have found it to be much more superior to old school spell checking tools such as SymSpell since it uses LLMs and is thus contextual.

# SETUP
## Setting up a Google Cloud Project
Instructions from Google : https://developers.google.com/google-ads/api/docs/get-started/oauth-cloud-project

## Installing ChromeDriver
Download ChromeDriver from here : https://chromedriver.chromium.org/downloads
Make sure to download the version compatible with your version of chrome and place it in the main directory of the repo

## Generating tokens
You will need Google authentication tokens to use this API. These should be generated locally (where you can access Google Chrome in a browser). All you have to do is run the two scripts inside the `Local_Scripts` folder and the tokens will be generated automatically

## Running GSpell 
An example of how to run GSpell is in run_GSpell.ipynb. Optionally, you can provide it a ground truth version of the text to be corrected and it will return several metrics such as edit distance to analyze the performance of GSpell
