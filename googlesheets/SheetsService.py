from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request



class SheetsService:
	SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]


	def make_sheets_service(self):

		creds = None

		if os.path.exists("token.pickle"):
			with open('token.pickle', 'rb') as token:
				creds = pickle.load(token)
		if not creds or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				flow = InstalledAppFlow.from_client_secrets_file(
					os.path.abspath("credentials.json"), SheetsService.SCOPES)
				creds = flow.run_local_server(port=0)

			with open('token.pickle', 'wb') as token:
				pickle.dump(creds, token)

		service = build('sheets', 'v4', credentials=creds)

		return service
