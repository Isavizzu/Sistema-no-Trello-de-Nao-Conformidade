import csv

class Document:

    def __init__(self, file_name):
        self.file_name = file_name
        self.non_conformities = self.get_non_conformities()
        self.project_name = self.get_name(2)
        self.artefact_name = self.get_name(1)
        self.auditor_name = self.get_name(0)

    
    def get_name(self, number):
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',') 
                for row in reader:
                    return row[number]
        except Exception as e:
            print(f"Error reading file: {e}")
        

    def get_non_conformities(self):
        non_conformities = []
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',') 
                next(reader)
                next(reader)
                non_conformities = [row for row in reader if row[1] == "Não Conforme"]
        except Exception as e:
            print(f"Error reading file: {e}")
        return non_conformities
    
    
    def get_number_of_rows(self) -> int:
        try:
            with open(self.file_name, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.reader(file, delimiter=',') 
                next(reader)
                next(reader)
                return sum(1 for row in reader if row[1] != "Não Aplicável")
        except Exception as e:
            print(f"Error reading file: {e}")
            return 0  
    

