import re
import geopandas as gpd
import pandas as pd
import os
import math
import csv


class MasterSheetProcessor:
    """class that receives a master sheet dataframe
    and gets it into the format needed to make crop plans"""
    BOUNDARY_DIRECTORY = "F:\\Farm\\FarmDataAutomation\\boundaries"
    CROP_PLANS_DIRECTORY = "F:\\Farm\\FarmDataAutomation\\CropPlans"
    FARM_REGEX = re.compile(r'^Farm')
    FIELD_REGEX = re.compile(r'^Field')
    GROWER_REGEX = re.compile(r'([HSJ][ORZC])(?=-)')
    CROPS_TO_REMOVE = ["CREP", "WILDLIFE MIX", ""]


    def __init__(self, master_sheet, year):
        self.master_sheet = master_sheet
        self.year = year
        self.rotation_regex = re.compile(f'{self.year} SPRING')
        self.boundaries = []
        self.missing_boundaries = []

    def get_boundary_files(self):
        for file in os.listdir(MasterSheetProcessor.BOUNDARY_DIRECTORY):
            if (file.endswith(".shp")):
                self.boundaries.append(os.path.join(MasterSheetProcessor.BOUNDARY_DIRECTORY ,file))


    def reduce_columns(self):
        columns = self.master_sheet.columns.to_list()


        regexes = [self.rotation_regex, MasterSheetProcessor.FARM_REGEX, MasterSheetProcessor.FIELD_REGEX]

        matching_columns = [x for x in columns for y in regexes if y.search(x)]

        reduced_mastersheeet = self.master_sheet[matching_columns]

        return reduced_mastersheeet

    def process(self):
        reduced_columns_mastersheet = self.reduce_columns()

        headers = reduced_columns_mastersheet.columns.to_list()

        farm_index = next(headers.index(i) for i in headers 
                                 if MasterSheetProcessor.FARM_REGEX.search(i))

        field_index = next(headers.index(i) for i in headers 
                                 if MasterSheetProcessor.FIELD_REGEX.search(i))

        rotation_index = next(headers.index(i) for i in headers 
                                 if self.rotation_regex.search(i))


        #Removes crops we don't care about including blanks
        filtered_mastersheet = reduced_columns_mastersheet[~reduced_columns_mastersheet[f'{self.year} SPRING'].isin(MasterSheetProcessor.CROPS_TO_REMOVE)]

        filtered_mastersheet.rename({f'{self.year} SPRING':'Product'}, axis=1, inplace=True)

        self.get_boundary_files()


        for i in range(len(filtered_mastersheet.index)):
            dir_number = math.floor(i/300)+1
            dir_name = f"Crop Plans {dir_number}"

            full_directory = os.path.join(MasterSheetProcessor.CROP_PLANS_DIRECTORY,dir_name)

            os.makedirs(full_directory,exist_ok=True)

            farm = filtered_mastersheet.iloc[i, farm_index]
            field = filtered_mastersheet.iloc[i, field_index]
            
            grower = MasterSheetProcessor.GROWER_REGEX.match(farm).group(1)

            filtered_mastersheet.loc[i, 'Grower'] = grower

            field_tag = f"{farm}_{field}"
            field_tag_regex = re.compile(field_tag)

            try:
                matching_boundary = next(b for b in self.boundaries if field_tag_regex.search(b))
            except Exception:
                self.missing_boundaries.append([farm, field])
                continue

            cropplan_df = gpd.read_file(matching_boundary)

            cropplan_df['Grower'] = grower

            cropplan_df['Farm'] = farm

            cropplan_df['Field'] = field
            
            cropplan_df['Year'] = self.year

            cropplan_df['Operation'] = 'Planting Crop Plan'

            cropplan_df['Product'] = filtered_mastersheet.loc[i, 'Product']

            output_filename = f"{self.year}_CropPlans_{field_tag}.shp"

            output_fullpath = os.path.join(full_directory, output_filename)
            
            cropplan_df.to_file(output_fullpath)

        
        self.write_missing_boundaries_file()
        print("Done")
            
    def write_missing_boundaries_file(self):
        missing_bound_file = os.path.join(MasterSheetProcessor.BOUNDARY_DIRECTORY,"_missing_boundaries.csv")

        with open(missing_bound_file, "w+", newline='') as file:
            writer = csv.writer(file, delimiter=",")

            writer.writerow(["Farm", "Field"])

            for row in self.missing_boundaries:
                writer.writerow(row)
        

