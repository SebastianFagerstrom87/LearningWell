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
        data_dict = self.filtered_data.to_dict('records')
        filtered_dict = [i for i in data_dict if not i[COUNTRY_COLUMN] == 'ALL']
        return filtered_dict

    def get_max_value(self):
        return self.filtered_data.loc[self.filtered_data[COUNTRY_COLUMN].eq('ALL'),
                                      VALUE_COLUMN].item()

    def print_chart(self, year, gender):
        os.system('cls')
        max_value = self.get_max_value()
        max_value_string = f'{max_value:.0f}'
        data_dict = self.get_dictionary_from_dataset()

        y_axis_first_row = f' {max_value_string} |'
        y_axis_middle_row = f'{"|" : >{len(y_axis_first_row)}}'
        y_axis_last_row = f' {"0" : >{len(max_value_string)}} |'
        total_chart_width = len(y_axis_first_row) + len(data_dict)*(COL_WIDTH+1)

        # Printing of data
        title = f'Planned care abroad for gender: {gender} and year: {year}'
        print('\n' + f'{title: ^{total_chart_width}}')
        row_segment = max_value / CHART_ROWS
        for row_nr in range(CHART_ROWS):
            # Three different ways to print y_axis. First, middle ones and last row.
            line = (y_axis_first_row if row_nr == 0
                    else ( y_axis_last_row if row_nr == (CHART_ROWS-1) else  y_axis_middle_row))
            for item in data_dict:
                # Content of chart cells can be empty, value or bar-filler
                if item[VALUE_COLUMN] > (CHART_ROWS-row_nr)*row_segment:
                    line += f'{"x": ^{COL_WIDTH}}|'
                elif item[VALUE_COLUMN] > (CHART_ROWS-row_nr-1)*row_segment:
                    value_string = f'{item[VALUE_COLUMN]:.0f}'
                    line += f'{value_string: ^{COL_WIDTH}}|'
                else:
                    line += f'{" ":>{COL_WIDTH}}|'
            print(line)

        x_axis_values = y_axis_middle_row
        separator = f'{"   ":-<{len(y_axis_first_row)}}'
        for item in data_dict:
            separator += f'{"-":->{COL_WIDTH}}-'
            x_axis_values += f'{item[COUNTRY_COLUMN]: ^{COL_WIDTH}}|'

        print(separator)
        print(x_axis_values)

def main():
    # Init data class for remote data
    data = RemoteData(REQUEST_URL)

    # Handle selection of year
    print("Statistics are available for following years: ", 
        data.get_unique_values_in_column(YEAR_COLUMN))
    selected_year = input("Please enter desired year: ")
    if selected_year not in data.get_unique_values_in_column(YEAR_COLUMN):
        print("Selected year not available!")
        quit()

    # Handle selection of gender
    print("Statistics can be presented for following genders: ", 
        data.get_unique_values_in_column(GENDER_COLUMN))
    selected_gender = input("Please enter desired gender: ")
    if selected_gender not in data.get_unique_values_in_column(GENDER_COLUMN):
        print("Selected gender not available!")
        quit()

    # Filter due to user input
    data.filter_inclusive(YEAR_COLUMN, selected_year)
    data.filter_inclusive(GENDER_COLUMN, selected_gender)

    # Print filtered data
    data.print_chart(selected_year, selected_gender)

if __name__ == "__main__":
    main()
