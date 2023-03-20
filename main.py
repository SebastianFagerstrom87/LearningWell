import requests
import json
import os
from pandas import json_normalize

REQUEST_URL = 'https://www.forsakringskassan.se/fk_apps/MEKAREST/public/v1/iv-planerad/IVplaneradvardland.json'
YEAR_COLUMN = 'dimensions.ar'
GENDER_COLUMN = 'dimensions.kon_kod'
DATA_DELETED_COLUMN = 'observations.antal.rojd'
COUNTRY_COLUMN = 'dimensions.vardland_kod'
VALUE_COLUMN = 'observations.antal.value'
CHART_ROWS = 25
COL_WIDTH = 4

class RemoteData:
    def __init__(self, url):
        self.url = url
        self.original_data = None
        self.filtered_data = None
        self.fetch()
        self.remove_missing_values()
  
    def filter_inclusive(self, column, value):
        self.filtered_data = \
            self.filtered_data.loc[self.filtered_data[column].eq(value)]
    
    def fetch(self):
        response = requests.get(REQUEST_URL)
        self.original_data = self.filtered_data = json_normalize(response.json())
        #print(self.original_data.to_string())

    def remove_missing_values(self):
        self.filter_inclusive(DATA_DELETED_COLUMN, False)

    def get_unique_values_in_column(self, column):
        return self.filtered_data[column].drop_duplicates().values.tolist()

    def get_dictionary_from_dataset(self):
        dict = self.filtered_data.to_dict('records')
        filtered_dict = [i for i in dict if not (i[COUNTRY_COLUMN] == 'ALL')]
        return filtered_dict
        
    def get_max_value(self):
        return self.filtered_data.loc[self.filtered_data[COUNTRY_COLUMN].eq('ALL'), VALUE_COLUMN].item()


    def print_chart(self, year, gender):
        os.system('cls')
        max_value = self.get_max_value()
        max_value_string = f'{max_value:.0f}'
        dict = self.get_dictionary_from_dataset()

        first_row = f' {max_value_string} |'
        middle_row = f'{"|" : >{len(first_row)}}'
        last_row = f' {"0" : >{len(max_value_string)}} |'
        total_chart_width = len(first_row) + len(dict)*(COL_WIDTH+1)

        title = f'Planned care abroad for gender: {gender} and year: {year}'
        print('\n' + f'{title: ^{total_chart_width}}')

        row_segment = max_value / CHART_ROWS
        for i in range(CHART_ROWS):
            line = (first_row if i == 0 else ( last_row if i == (CHART_ROWS-1) else  middle_row))
            for j in range(len(dict)):
                if dict[j][VALUE_COLUMN] > (CHART_ROWS-i)*row_segment:
                    line += f'{"x": ^{COL_WIDTH}}|' # Set center!
                elif dict[j][VALUE_COLUMN] > (CHART_ROWS-i-1)*row_segment:
                    value_string = f'{dict[j][VALUE_COLUMN]:.0f}'
                    line += f'{value_string: ^{COL_WIDTH}}|'
                else:
                    line += f'{" ":>{COL_WIDTH}}|'
            print(line)

        axis_values = middle_row
        separator = f'{"   ":-<{len(first_row)}}'
        for i in range(len(dict)):
            separator += f'{"-":->{COL_WIDTH}}-'
            axis_values += f'{dict[i][COUNTRY_COLUMN]: ^{COL_WIDTH}}|'

        print(separator)
        print(axis_values)

def main():
    data = RemoteData(REQUEST_URL)
    
    print("Statistics are available for following years: ", 
        data.get_unique_values_in_column(YEAR_COLUMN))
    selected_year = input("Please enter desired year: ")
    if selected_year not in data.get_unique_values_in_column(YEAR_COLUMN):
        print("Selected year not available!")
        quit()
    
    print("Statistics can be presented for following genders: ", 
        data.get_unique_values_in_column(GENDER_COLUMN))
    selected_gender = input("Please enter desired gender: ")
    if selected_gender not in data.get_unique_values_in_column(GENDER_COLUMN):
        print("Selected gender not available!")
        quit()

    data.filter_inclusive(YEAR_COLUMN, selected_year)
    data.filter_inclusive(GENDER_COLUMN, selected_gender)

    data.print_chart(selected_year, selected_gender)

if __name__ == "__main__":
    main()