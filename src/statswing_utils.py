import pandas as pd
from src.config import TEAM_NAME_MAPPING, STAT_MAPPING, STAT_DESCRIPTIONS

def load_data(file_path: str) -> pd.DataFrame:
    '''

    Loads the player data from a CSV file
    
    '''
    try:
        data = pd.read_csv(file_path)
        return data
    except FileNotFoundError:
        print(f'Error: The file {file_path} could not be found.')
        return
    
def find_player(data: pd.DataFrame, name: str) -> pd.DataFrame:
    '''
    
    Finds a player in the dataset by name

    '''
    return data[data["Name"] == name]

def get_dataset_column(stat_name: str) -> str:
    '''
    
    Retrieves the corresponding dataset column name for a given stat alias
    
    '''
    alias_to_col = {alias: column for column, alias in STAT_MAPPING.items()}
    return alias_to_col.get(stat_name, stat_name)