from model import ETLModel
from view import ETLView


class ETLController:
    def __init__(self):
        self.model = ETLModel()
        self.view = ETLView(self)
        self.view.show()

    def run_etl(self):
        try:
            s3_path = self.view.file_path_var.get()
            metadata = {
                "user_id": 1,
                "genetic_line": self.view.genetic_line.get().strip(),
                "sex": self.view.sex.get().strip(),
                "age_weeks": self.view.age_weeks.get().strip(),
                "device_id": 1,
                "name": self.view.name_var.get().strip(),
                "meninges": self.view.flags["meninges"].get(),
                "brain": self.view.flags["brain"].get(),
                "superior_sagittal_sinus": self.view.flags["sss"].get(),
                "confluence_of_sinuses": self.view.flags["confluence_of_sinuses"].get(),
                "transverse_sinus": self.view.flags["transverse_sinus"].get(),
                "cortex": self.view.flags["cortex"].get(),
                "thalamus": self.view.flags["thalamus"].get(),
                "hypothalamus": self.view.flags["hypothalamus"].get(),
            }
            self.model.run_etl(s3_path, metadata)
            self.view.show_success("Файл и метаданные успешно загружены!")
        except Exception as e:
            self.view.show_error(str(e))
