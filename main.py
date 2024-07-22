import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QLineEdit,
                             QPushButton, QComboBox, QListWidget, QFrame, QHBoxLayout, QWidget, QMessageBox)
from PyQt6.QtGui import QPixmap, QImage, QIcon
from PyQt6.QtCore import Qt, pyqtSlot, QMetaObject, Q_ARG, Q_RETURN_ARG, QTimer, QPointF
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PIL import Image
import threading
import os
import json
from datetime import datetime
import glob
from prompt_analysis import CompanyInfoExtractor
from retrieve_text_from_pdf import PdfTextProcessor
from retrieve_text_from_bildirim import BildirimTextProcessor


class PdfViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(800, 600) 
        self.setWindowTitle("Soru Penceresi")
        self.setGeometry(100, 100, 800, 600)
        self.history_listbox = None
        self.pdf_text_processor = PdfTextProcessor()
        self.bildirim_text_processor = BildirimTextProcessor()
        self.notification_pdfs = []
        self.notification_jsons = []
        self.pdf_doc = QPdfDocument(self)
        self.current_pdf_path = ""
        self.pages_text = None
        self.current_page = 0
        self.previous_prompts = []
        self.extracted_notification_info = None
        self.companies_file_paths = {
            "company_names": "companies_info/finalsirketler.txt",
            "abbreviations": "companies_info/finalkisaltmalar.txt",
            "notification_types": "companies_info/bildirim.txt"
        }

        self.prompt_extractor = CompanyInfoExtractor(self.companies_file_paths)
        self.setup_ui()

    def setup_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.create_related_pages_label()
        self.create_history_listbox()
        self.create_combo_box()
        self.create_page_navigation()
        self.create_loading_label()
        self.create_question_frame()
        self.create_pdf_viewer()
        self.create_zoom_buttons()

        self.resizeEvent(None)

    def resizeEvent(self, event):
        width = self.width()
        height = self.height()
        self.update_question_frame_placement(width, height)
        self.update_history_listbox_placement(width, height)
        self.update_related_pages_placement(width, height)
        self.update_combo_box_placement(width, height)
        self.update_page_navigation_label_placement(width, height)
        self.update_pdf_viewer(width,height)
        self.update_zoom_buttons_placement()


    def update_pdf_viewer(self,width,height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800

        pdf_viewer_x = int(285 * width_scale_factor)
        pdf_viewer_y = int(95 * height_scale_factor)
        pdf_viewer_width = int(487 * width_scale_factor)
        pdf_viewer_height = int(390 * height_scale_factor)

        self.pdf_viewer.setGeometry(pdf_viewer_x, pdf_viewer_y, pdf_viewer_width, pdf_viewer_height)


    def create_related_pages_label(self):
        self.related_pages_label = QLabel("Alakalı Sayfalar", self.central_widget)
        self.related_pages_label.move(285, 25)

    def create_history_listbox(self):
        self.history_listbox = QListWidget(self.central_widget)
        self.history_listbox.setGeometry(20, 50, 250, 470)
        self.history_listbox.itemClicked.connect(self.load_past_prompt_result)

    def create_combo_box(self):
        self.combo_box = QComboBox(self.central_widget)
        self.combo_box.setGeometry(280, 50, 500, 30)
        self.combo_box.currentIndexChanged.connect(self.on_combobox_select)

    def create_page_navigation(self):
        self.page_navigation_frame = QFrame(self.central_widget)
        self.page_navigation_frame.setGeometry(285, 490, 250, 40)
        layout = QHBoxLayout()
        self.page_navigation_frame.setLayout(layout)

        self.previous_button = QPushButton("Önceki Sayfa", self.page_navigation_frame)
        self.previous_button.clicked.connect(self.show_previous_page)
        layout.addWidget(self.previous_button)

        self.next_button = QPushButton("Sonraki Sayfa", self.page_navigation_frame)
        self.next_button.clicked.connect(self.show_next_page)
        layout.addWidget(self.next_button)

        self.jump_button = QPushButton("Sayfaya Atla", self.page_navigation_frame)
        self.jump_button.clicked.connect(self.jump_to_page)
        layout.addWidget(self.jump_button)

        self.page_entry = QLineEdit(self.page_navigation_frame)
        self.page_entry.setFixedWidth(50)
        self.page_entry.setFixedHeight(20)
        self.page_entry.returnPressed.connect(self.jump_to_page)
        layout.addWidget(self.page_entry)

    def create_loading_label(self):
        self.loading_label = QLabel(self.central_widget)
        self.loading_label.move(40, 20)

    def create_question_frame(self):
        self.question_frame = QFrame(self.central_widget)
        self.question_frame.setGeometry(20, 550, 760, 40)
        layout = QHBoxLayout()
        self.question_frame.setLayout(layout)

        self.question_entry = QLineEdit(self.question_frame)
        self.question_entry.setFixedWidth(700)
        self.question_entry.setFixedHeight(20)
        self.question_entry.returnPressed.connect(self.on_send_with_adding_history)
        layout.addWidget(self.question_entry)

        self.send_button = QPushButton("Sor", self.question_frame)
        self.send_button.clicked.connect(self.on_send_with_adding_history)
        layout.addWidget(self.send_button)

    def create_pdf_viewer(self):
        self.pdf_viewer = QPdfView(self.central_widget)
        self.pdf_viewer.setGeometry(285, 120, 500, 360)
        self.pdf_viewer.setDocument(self.pdf_doc)

    def create_zoom_buttons(self):
        self.zoom_in_button = QPushButton(self.pdf_viewer)
        self.zoom_in_button.setIcon(QIcon("icons/zoom_in.png"))
        self.zoom_in_button.setToolTip("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)

        self.zoom_out_button = QPushButton(self.pdf_viewer)
        self.zoom_out_button.setIcon(QIcon("icons/zoom_out.png"))
        self.zoom_out_button.setToolTip("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)

        self.zoom_in_button.setStyleSheet("background-color: rgba(128, 128, 128, 128); border: none;")
        self.zoom_out_button.setStyleSheet("background-color: rgba(128, 128, 128, 128); border: none;")

    def update_zoom_buttons_placement(self):
        pdf_viewer_rect = self.pdf_viewer.geometry()
        button_size = 40
        spacing = 10  # Space between the buttons
        self.zoom_out_button.setGeometry((pdf_viewer_rect.width() - 2 * button_size - spacing) - 10, (pdf_viewer_rect.height() - button_size) - 10, button_size, button_size)
        self.zoom_in_button.setGeometry((pdf_viewer_rect.width() - button_size) - 10,( pdf_viewer_rect.height() - button_size)-10, button_size, button_size)

    def zoom_in(self):
        current_zoom = self.pdf_viewer.zoomFactor()
        new_zoom = current_zoom + 0.1
        new_zoom = min(new_zoom, 5.0)  # Maximum zoom limit
        self.pdf_viewer.setZoomFactor(new_zoom)

    def zoom_out(self):
        current_zoom = self.pdf_viewer.zoomFactor()
        new_zoom = current_zoom - 0.1
        new_zoom = max(new_zoom, 0.1)  # Minimum zoom limit
        self.pdf_viewer.setZoomFactor(new_zoom)

    def update_question_frame_placement(self, width, height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800
        self.question_frame.setGeometry(20, int(550 * height_scale_factor), int(760 * width_scale_factor), 40)
        self.question_entry.setFixedWidth(int(600 * width_scale_factor))
        self.send_button.setFixedWidth(int(120 * width_scale_factor))

    def update_history_listbox_placement(self, width, height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800
        self.history_listbox.setGeometry(20, 50, int(250 * width_scale_factor), int(470 * height_scale_factor))

    def update_related_pages_placement(self, width, height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800
        self.related_pages_label.setGeometry(int(285 * width_scale_factor), 25, 200, 30)

    def update_combo_box_placement(self, width, height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800
        self.combo_box.setGeometry(int(280 * width_scale_factor), 50, int(500 * width_scale_factor), 30)

    def update_page_navigation_label_placement(self, width, height):
        height_scale_factor = height / 600
        width_scale_factor = width / 800
        self.page_navigation_frame.setGeometry(int(285 * width_scale_factor + (250 * width_scale_factor - 250)), int(490 * height_scale_factor), 500, 40)

    def load_past_prompt_result(self, item):
        selected_index = self.history_listbox.row(item)
        self.question_entry.setText(self.previous_prompts[selected_index])
        self.on_send_without_adding_history()

    def extract_text_from_pdf(self, pdf_path):
        doc = fitz.open(pdf_path)
        pages_text = {page_num: doc.load_page(page_num).get_text() for page_num in range(len(doc))}
        return doc, pages_text

    def get_most_relevant_pdf_pages(self, pdf_files, json_files, question):
        relevant_pages = []
        for pdf_file_path in pdf_files:
            relevant_page_0, relevant_page_1, similarities, indices = self.pdf_text_processor.get_most_relevant_two_pages(pdf_file_path, question)
            if relevant_page_0 is not None:
                relevant_pages.append((pdf_file_path, indices[0] + 1, similarities[0]))
            if relevant_page_1 is not None:
                relevant_pages.append((pdf_file_path, indices[1] + 1, similarities[1]))

        for json_file_path in json_files:
            base = os.path.splitext(json_file_path)[0]
            file_name = base + ".pdf"
            relevant_page_0, relevant_page_1, similarities, indices = self.bildirim_text_processor.get_most_relevant_two_pages(file_name, question)
            if relevant_page_0 is not None:
                relevant_pages.append((file_name, 1, similarities[0]))
            if relevant_page_1 is not None:
                relevant_pages.append((file_name, 1, similarities[1]))

        relevant_pages.sort(key=lambda x: x[2], reverse=True)
        return [(pdf_path, page_number) for pdf_path, page_number, _ in relevant_pages[:10]]

    def show_page(self, pdf_path, page_num):
        self.loading_label.clear()
        self.send_button.setEnabled(False)
        self.pdf_viewer.setVisible(False)  # Make PDF viewer invisible

        def load_and_show_page():
            try:
                self.pdf_doc.load(pdf_path)
                if page_num < 1 or page_num > self.pdf_doc.pageCount():
                    raise ValueError(f"Geçersiz sayfa numarası: {page_num}. PDF toplam {self.pdf_doc.pageCount()} sayfa içeriyor.")

                self.current_pdf_path = pdf_path
                self.current_page = page_num
                self.pdf_viewer.setDocument(self.pdf_doc)
                page_navigator = self.pdf_viewer.pageNavigator()
                page_navigator.jump(self.current_page - 1, QPointF(0, 0))
                self.send_button.setEnabled(True)
                self.pdf_viewer.setVisible(True)  # Make PDF viewer visible again
                self.loading_label.clear()  # Clear loading message
                print(f"Showing page {self.current_page} from {self.current_pdf_path}")
            except Exception as e:
                self.handle_error(str(e))
                self.pdf_viewer.setVisible(True)  # Ensure PDF viewer is visible in case of error

        QTimer.singleShot(0, load_and_show_page)

    def show_loading_message(self):
        width = self.width()
        height = self.height()
        height_scale_factor = height / 600
        width_scale_factor = width / 800

        self.loading_label.setText("Sorunuza dair sayfa getiriliyor...")
        self.loading_label.setStyleSheet("font-size: {}px; font-style: italic;".format(int(16 * width_scale_factor)))
        self.loading_label.move(int(440 * width_scale_factor), int(280 * height_scale_factor))
        self.loading_label.raise_()  # Bring loading label to front
        self.loading_label.setVisible(True)  # Ensure loading label is visible
        self.pdf_viewer.setVisible(False)  # Make PDF viewer invisible during loading




    def handle_error(self, error_message):
        QMessageBox.critical(self, "PDF Açarken Hata", f"Hata: {error_message}")
        self.send_button.setEnabled(True)



    def get_notification_folder_path(self, company_folder_path, notification):
        notification_type = notification["notification_type"]
        extracted_dates = notification["extracted_dates"]
        extracted_date_start = extracted_dates[0]
        extracted_date_end = extracted_dates[1] if len(extracted_dates) == 2 else None

        try:
            folder_names = [name for name in os.listdir(company_folder_path) if os.path.isdir(os.path.join(company_folder_path, name))]
        except FileNotFoundError:
            QMessageBox.critical(self, "Dosya Hatası", f"Dizin bulunamadı: {company_folder_path}")
            return []

        selected = []
        for folder in folder_names:
            with open(f"{company_folder_path}/{folder}/{folder}.json", 'r', encoding='utf-8') as file:
                data = json.load(file)

            girizgah_data = data["girizgah"]
            bildirim = girizgah_data["bildirim_türü"]
            tarih = girizgah_data["tarih"].split()[0]

            date_obj = datetime.strptime(tarih, "%d.%m.%Y")

            if extracted_date_end:
                if extracted_date_start <= date_obj <= extracted_date_end and (bildirim == notification_type or notification_type == "TB"):
                    selected.append(f"{company_folder_path}/{folder}")
            else:
                if date_obj == extracted_date_start and (bildirim == notification_type or notification_type == "TB"):
                    selected.append(f"{company_folder_path}/{folder}")

        return selected


    def get_notification_files(self, notification, file_extension):
        self.extracted_notification_info = self.prompt_extractor.get_extracted_notification_info(notification)
        selected_abbrev = self.extracted_notification_info["selected_abbrev"]
        company_folder_path = f"./sirketler/{selected_abbrev}"

        notification_folder_path_list = self.get_notification_folder_path(company_folder_path, self.extracted_notification_info)
        doc_list = []
        for notification_folder_path in notification_folder_path_list:
            doc_list.extend(glob.glob(f'{notification_folder_path}/*.{file_extension}'))

        return doc_list

    def open_pdf_for_notification(self):
        notification = self.question_entry.text().strip()
        if not notification:
            QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Bildirim Girilmedi", "Lütfen bildirimi girerek tekrar deneyiniz."))
            return

        self.notification_pdfs = self.get_notification_files(notification, 'pdf')
        if not self.notification_pdfs:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "PDF Bulunamadı", f"'{notification}' bildirimiyle alakalı hiçbir PDF dosyası bulunamadı."))
            return

        self.notification_jsons = self.get_notification_files(notification, 'json')
        if not self.notification_jsons:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "JSON Bulunamadı", f"'{notification}' bildirimiyle alakalı hiçbir JSON dosyası bulunamadı."))
            return

        try:
            QTimer.singleShot(0, lambda: self.pdf_doc.load(self.notification_pdfs[0]))
            self.current_page = 1
        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.critical(self, "PDF Açarken Hata", f"Hata: {str(e)}"))
            return


    def on_send_without_adding_history(self, item=None):
        if item:
            selected_index = self.history_listbox.row(item)
            self.question_entry.setText(self.previous_prompts[selected_index])
        
        question = self.question_entry.text()
        if not question:
            QMessageBox.warning(self, "Soru Girilmedi", "Lütfen sorunuzu girerek tekrar deneyiniz.")
            self.send_button.setEnabled(True)
            return

        self.send_button.setEnabled(False)
        self.show_loading_message()

        # Run the prompt handling logic directly
        self.handle_prompt(question)

        # Re-enable the send button after handling the prompt
        self.send_button.setEnabled(True)



    def on_send_with_adding_history(self):
        question = self.question_entry.text()
        if not question:
            QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Soru Girilmedi", "Lütfen sorunuzu girerek tekrar deneyiniz."))
            return

        QTimer.singleShot(0, lambda: self.send_button.setEnabled(False))
        self.show_loading_message()
        QTimer.singleShot(0, lambda: self.history_listbox.addItem(question))
        self.previous_prompts.append(question)
        QTimer.singleShot(0, lambda: self.handle_prompt(question))

    def handle_prompt(self, prompt):
        def run():
            self.open_pdf_for_notification()
            self.process_question(self.extracted_notification_info["question"])

        QTimer.singleShot(0, run)

    def process_question(self, question):
        related_pages = self.get_most_relevant_pdf_pages(self.notification_pdfs, self.notification_jsons, question)
        if related_pages:
            self.current_page = related_pages[0][1]
            self.update_combobox(related_pages)
            self.show_page(related_pages[0][0], related_pages[0][1])
        else:
            self.loading_label.clear()
            QMessageBox.warning(self, "Alakalı Sayfa Bulunamadı", "Girdiğiniz soruyla alakalı hiçbir sayfa bulunamadı.")
            self.send_button.setEnabled(True)



    def update_combobox(self, related_pages):
        self.combo_box.clear()
        for pdf, page in related_pages:
            self.combo_box.addItem(f"{os.path.basename(pdf)} - Page {page}")

    def on_combobox_select(self, index):
        selected = self.combo_box.itemText(index)
        if selected:
            pdf_name, page_str = selected.split(' - Page ')
            page_num = int(page_str)
            for pdf_path in self.notification_pdfs:
                if os.path.basename(pdf_path) == pdf_name:
                    self.show_page(pdf_path, page_num)
                    break

    def jump_to_page(self):
        try:
            page_number = int(self.page_entry.text())
            self.current_page = page_number
            self.show_page(self.current_pdf_path, self.current_page)
        except ValueError:
            QMessageBox.information(self, "Geçersiz Bilgi", "Geçerli bir sayfa numarası girin")

    def show_next_page(self):
        if not self.current_pdf_path:
            QMessageBox.information(self, "Hata", "Öncelikle bir PDF dosyası açmalısınız.")
            return

        if self.current_page < self.pdf_doc.pageCount():
            self.current_page += 1
            self.show_page(self.current_pdf_path, self.current_page)
        else:
            QMessageBox.information(self, "Belge Sonu", "Belgenin sonuna ulaştınız.")
        print(f"Current page (next): {self.current_page}")

    def show_previous_page(self):
        if not self.current_pdf_path:
            QMessageBox.information(self, "Hata", "Öncelikle bir PDF dosyası açmalısınız.")
            return

        if self.current_page > 1:
            self.current_page -= 1
            self.show_page(self.current_pdf_path, self.current_page)
        else:
            QMessageBox.information(self, "Belge Başı", "Belgenin başındasınız.")
        print(f"Current page (previous): {self.current_page}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PdfViewerApp()
    viewer.show()
    sys.exit(app.exec())
