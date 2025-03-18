from dataclasses import dataclass


@dataclass
class StatusMessage():
    s_404: str = "Not Found"
    successfull_save: str = "Data saved successfully"
    not_found_data: str = "Data not found"
    updated_successfully: str = "Data updated successfully"