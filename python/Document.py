import csv

class Document:

    def __init__(self, file_name):
        self.file_name = file_name
        self.non_conformities = self.get_non_conformities()
        

    def get_non_conformities(self):
        non_conformities = []
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',') 
                next(reader)  
                non_conformities = [row for row in reader if row[1] == "Não Conforme"]
        except Exception as e:
            print(f"Error lendo o file: {e}")
        return non_conformities
    
    
    def get_number_of_rows(self) -> int:
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',') 
                next(reader)  
                return sum(1 for row in reader if row[1] != "Não Aplicável")
        except Exception as e:
            print(f"Error reading file: {e}")
            return 0  
    

