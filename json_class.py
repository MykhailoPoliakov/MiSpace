import json
import os

class Json:
    """
    Attributes:
        self.data (dict)
            to change data in default_data

    Methods:
        self.update_data()
            to save changes in self.data to the json file

    Args:
        app_name (str): main file name for creating folder in local app data
            Example: "App"
        file_name (str): json file name with .json
            Example: "info.json"
        default_data (dict): Starting dictionary, creates file if not founded
            Example: { info1 = None, info2 = None }
    """
    def __init__(self, app_name: str, file_name : str, default_data: dict) -> None:
        self.__app_name = app_name
        self.__file_name = file_name
        self.__default_dict = default_data
        # get user data from the file
        self.data = self.__get_data
        self.update_data()

    @property
    def __path(self) -> str:
        """ get path that works with compiling """
        save_dir = os.path.join(os.getenv("LOCALAPPDATA"), self.__app_name)
        os.makedirs(save_dir, exist_ok=True)
        return os.path.join(save_dir, self.__file_name)

    @property
    def __get_data(self) -> dict:
        """ get data from json file, if no data, get data from default dict """
        try:
            with open(self.__path, "r", encoding="utf-8") as json_file:
                return json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            return self.__default_dict

    def update_data(self) -> None:
        """ after changing self.data update date in json file """
        with open(self.__path, "w", encoding="utf-8") as _json_file:
            json.dump(self.data, _json_file, ensure_ascii=False, indent=4, sort_keys=True)