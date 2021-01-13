from googlesheets.GoogleSheet import GoogleSheet
from MasterSheetProcessor import MasterSheetProcessor


def main():
	YEAR = input("Enter the year you want to run crop plans for: ")

	gs = GoogleSheet(
		spreadsheet_id='1AUMOHvJnfGT5Ve1Ep-ECslC9bhj8sP0DAI64CmQ-iWw',
		sheet_range="Master Sheet")
	
	df = gs.create_dataframe()

	processor = MasterSheetProcessor(df,YEAR)

	processor.process()
	


if __name__ == '__main__':
	main()