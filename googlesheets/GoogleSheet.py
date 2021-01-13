from googlesheets.SheetsService import SheetsService
import pandas as pd

class GoogleSheet:
    """This class is used for creating google sheet objects"""

    def __init__(self, spreadsheet_id, sheet_range):
        self.sheets_service = SheetsService().make_sheets_service()
        self.spreadsheet_id = spreadsheet_id
        self.sheet_range = sheet_range

    def get_values(self):
        sheet = self.sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=self.spreadsheet_id, range=self.sheet_range).execute()

        values = result.get('values', [])

        if not values:
            raise Exception('No values')
        else:
            return values

    def create_dataframe(self):
        values = self.get_values()
        headers = values.pop(0)
        df = pd.DataFrame(values, columns=headers)
        
        return df


