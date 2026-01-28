from model import ETlModel
from view import ETLView


class ETLController:
    def __init__(self, root):
        self.model = ETlModel()
        self.view = ETLView(root, self)

    def choose_file(self):
        s3_path = self.view.choose_file()
        if s3_path:
            self.view.file_path_var.set(s3_path)

    def run_etl(self):
        try:
            s3_path = self.view.file_path_var.get()
            folder = self.view.folder_var.get()
            name = self.view.name_var.get()
            genetic_line = self.genetic_line.get()
            sex = self.sex.get()
            age = self.age_weeks.get()
            metadata = {
                "user_id": 2,
                "genetic_line": genetic_line.strip(),
                "sex": sex.strip,
                "age_weeks": 12,
                "device_id": 1,
                "name": name.strip(),
                "meninges": self.view.flags["meninges"].get(),
                "brain": self.view.flags["brain"].get(),
                "superior_sagittal_sinus": self.view.flags["sss"].get(),
                "confluence_of_sinuses": False,
                "transverse_sinus": self.view.flags["transverse_sinus"].get(),
                "cortex": self.view.flags["cortex"].get(),
                "thalamus": self.view.flags["thalamus"].get(),
                "hypothalamus": False,
                "experiment_id": 2,
            }

            result = self.model.run_etl(s3_path, folder, metadata)
        except Exception as e:
            self.view.show_error(str(e))
