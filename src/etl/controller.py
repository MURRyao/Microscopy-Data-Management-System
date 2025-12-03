from model import ETlModel
from view import ETLView


class ETLController:
    def __init__(self, root):
        self.model = ETlModel
        self.view = ETLView(root, self)

    def choose_file(self):
        s3_path = self.view.choose_file_dialog()
        if s3_path:
            self.view.file_path_var.set(s3_path)

    def run_etl(self):
        try:
            s3_path = self.view.get_file_path()
            folder = self.view.get_folder()
            name = self.view.get_name()
            metadata = {
                "mouse_id": 1,
                "experiment_id": 1,
                "name": self.name_var.get().strip(),
                "meninges": self.flags["meninges"].get(),
                "brain": self.flags["brain"].get(),
                "sss": self.flags["sss"].get(),
                "transverse_sinus": self.flags["transverse_sinus"].get(),
                "cortex": self.flags["cortex"].get(),
                "thalamus": self.flags["thalamus"].get(),
            }
            result = self.model.run_etl(s3_path, folder, metadata)
            self.view.show_success(result)
        except Exception as e:
            self.view.show_error(str(e))
