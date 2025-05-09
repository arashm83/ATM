import sys
import csv
from dataclasses import dataclass
from abc import abstractmethod
from typing import List, Optional
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout,
    QLabel, QPushButton, QLineEdit, QGridLayout, QMessageBox,
    QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


@dataclass
class User:
    card_number: str
    password: str
    balance: int

    @staticmethod
    def load_users(file_name):
        users = []
        with open(file_name, 'r') as f:
            for line in f:
                card, passwd, balance = line.split(',')
                users.append(User(card, passwd, int(balance)))
        return users
    @staticmethod
    def save(file_name, users):
        with open(file_name, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerows((user.card_number, user.password, user.balance) for user in users)


class BankService:
    def __init__(self, users: List[User]):
        self._users = users
        self._current_user = None

    def authenticate(self, password: str) -> Optional[User]:
        for user in self._users:
            if user.password == password:
                self._current_user = user
                return user
        return None

    @property
    def current_user(self) -> Optional[User]:
        return self._current_user

    def change_password(self, current_pass: str, new_pass: str) -> bool:
        if not self._current_user or self._current_user.password != current_pass:
            return False
        self._current_user.password = new_pass
        return True

    def withdraw(self, amount: int) -> bool:
        if not self._current_user or amount <= 0 or self._current_user.balance < amount:
            return False
        self._current_user.balance -= amount
        return True

    def transfer(self, amount: int, dest_card: str) -> bool:
        if (not self._current_user or amount <= 0 or
            not dest_card.isdigit() or 
            self._current_user.balance < amount):
            return False
        self._current_user.balance -= amount
        return True

    def get_balance(self) -> int:
        return self._current_user.balance if self._current_user else 0


# --------------language_manager-----------------
class LanguageManager:
    PERSIAN = "fa"
    ENGLISH = "en"
    
    def __init__(self):
        self.current_language = self.PERSIAN
        self._translations = {
            self.PERSIAN: {
                "language_selection": "زبان خود را انتخاب کنید",
                "enter_password": "لطفاً رمز خود را وارد کنید",
                "password_placeholder": "رمز عبور",
                "submit": "تایید",
                "wrong_password": "رمز عبور اشتباه است",
                "withdraw": "برداشت وجه",
                "transfer": "انتقال وجه",
                "balance": "اعلام موجودی",
                "change_password": "تغییر رمز",
                "exit": "خروج",
                "select_amount": "مبلغ مورد نظر را انتخاب کنید",
                "custom_amount": "مبلغ دلخواه",
                "back": "بازگشت",
                "enter_amount": "مبلغ مورد نظر را وارد کنید:",
                "enter_dest_card": "شماره کارت مقصد را وارد کنید:",
                "confirm": "تایید",
                "current_password": "رمز فعلی را وارد کنید:",
                "new_password": "رمز جدید را وارد کنید:",
                "operation_success": "عملیات با موفقیت انجام شد",
                "new_operation": "عملیات جدید",
                "insufficient_balance": "موجودی کافی نیست",
                "invalid_amount": "مبلغ نامعتبر است",
                "invalid_card": "شماره کارت نامعتبر است",
                "password_changed": "رمز عبور با موفقیت تغییر یافت",
                "password_change_failed": "تغییر رمز ناموفق بود",
                "your_balance": "موجودی شما:"
            },
            self.ENGLISH: {
                "language_selection": "Choose your language",
                "enter_password": "Please enter your password",
                "password_placeholder": "Password",
                "submit": "Submit",
                "wrong_password": "Wrong password",
                "withdraw": "Withdraw Cash",
                "transfer": "Money Transfer",
                "balance": "Account Balance",
                "change_password": "Change Password",
                "exit": "Exit",
                "select_amount": "Select amount",
                "custom_amount": "Custom Amount",
                "back": "Back",
                "enter_amount": "Enter the desired amount:",
                "enter_dest_card": "Enter destination card number:",
                "confirm": "Confirm",
                "current_password": "Enter current password:",
                "new_password": "Enter new password:",
                "operation_success": "Operation completed successfully",
                "new_operation": "New Operation",
                "insufficient_balance": "Insufficient balance",
                "invalid_amount": "Invalid amount",
                "invalid_card": "Invalid card number",
                "password_changed": "Password changed successfully",
                "password_change_failed": "Password change failed",
                "your_balance": "Your balance:"
            }
        }
        
    
    def set_language(self, language: str):
        if language in [self.PERSIAN, self.ENGLISH]:
            self.current_language = language
    
    def get_text(self, key: str) -> str:
        return self._translations[self.current_language].get(key, key)
    
    def get_current_language(self):
        return self.current_language
    


# ------------GUI--------------
class BasePage(QWidget):
    back_requested = pyqtSignal()
    operation_completed = pyqtSignal(str)
    
    def __init__(self, language_manager: LanguageManager):
        super().__init__()
        self.lang = language_manager
        self.setup_ui()
        
    
    @abstractmethod
    def setup_ui(self):
        pass
    
    def show_message(self, title: str, message: str):
        QMessageBox.information(self, title, message)

    def update_text_ui(self, language):
        self.lang.current_language = language


class LanguageSelectionPage(BasePage):
    
    def setup_ui(self):
        layout = QVBoxLayout()
        label = QLabel("select language/ زبان خود را انتخاب کنید")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        btn_persian = QPushButton("فارسی")
        btn_persian.setFont(QFont("B-nazanin", 12))
        btn_persian.clicked.connect(lambda: self.select_language(LanguageManager.PERSIAN))
        
        btn_english = QPushButton("English")
        btn_english.setFont(QFont("B-nazanin", 12))
        btn_english.clicked.connect(lambda: self.select_language(LanguageManager.ENGLISH))
        
        layout.addWidget(label)
        layout.addWidget(btn_persian)
        layout.addWidget(btn_english)
        
        self.setLayout(layout)
    
    def select_language(self, language: str):
        self.lang.set_language(language)
        self.operation_completed.emit(language)


class LoginPage(BasePage):
    def __init__(self, language_manager: LanguageManager, bank_service: BankService):
        self.bank = bank_service
        super().__init__(language_manager)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        label = QLabel(self.lang.get_text("enter_password"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("B-nazanin", 16))
        
        self.password_input = QLineEdit()
        self.password_input.setFont(QFont("B-nazanin", 14))
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.password_input.setPlaceholderText(self.lang.get_text("password_placeholder"))
        
        submit_btn = QPushButton(self.lang.get_text("submit"))
        submit_btn.setFont(QFont("B-nazanin", 14))
        submit_btn.clicked.connect(self.authenticate)
        
        layout.addWidget(label)
        layout.addWidget(self.password_input)
        layout.addWidget(submit_btn)
        
        self.setLayout(layout)
    
    def authenticate(self):
        password = self.password_input.text()
        if self.bank.authenticate(password):
            self.operation_completed.emit("login_success")
        else:
            self.show_message("Error", self.lang.get_text("wrong_password"))
        self.password_input.clear()


class MenuPage(BasePage):
    def setup_ui(self):
        layout = QGridLayout()
        
        btn_withdraw = QPushButton(self.lang.get_text("withdraw"))
        btn_withdraw.setFont(QFont("B-nazanin", 14))
        btn_withdraw.clicked.connect(lambda: self.operation_completed.emit("withdraw"))
        
        btn_transfer = QPushButton(self.lang.get_text("transfer"))
        btn_transfer.setFont(QFont("B-nazanin", 14))
        btn_transfer.clicked.connect(lambda: self.operation_completed.emit("transfer"))
        
        btn_balance = QPushButton(self.lang.get_text("balance"))
        btn_balance.setFont(QFont("B-nazanin", 14))
        btn_balance.clicked.connect(lambda: self.operation_completed.emit("balance"))
        
        btn_change_pass = QPushButton(self.lang.get_text("change_password"))
        btn_change_pass.setFont(QFont("B-nazanin", 14))
        btn_change_pass.clicked.connect(lambda: self.operation_completed.emit("change_password"))
        
        btn_exit = QPushButton(self.lang.get_text("exit"))
        btn_exit.setFont(QFont("B-nazanin", 14))
        btn_exit.clicked.connect(lambda: self.operation_completed.emit("exit"))
        
        layout.addWidget(btn_withdraw, 0, 0)
        layout.addWidget(btn_transfer, 0, 1)
        layout.addWidget(btn_balance, 1, 0)
        layout.addWidget(btn_change_pass, 1, 1)
        layout.addWidget(btn_exit, 2, 0, 1, 2)
        
        self.setLayout(layout)


class WithdrawPage(BasePage):
    def __init__(self, language_manager: LanguageManager, bank_service: BankService):
        self.bank = bank_service
        super().__init__(language_manager)
    
    def setup_ui(self):
        layout = QGridLayout()
        
        label = QLabel(self.lang.get_text("select_amount"))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setFont(QFont("B-nazanin", 16))
        
        
        amounts = ["500,000", "1,000,000", "1,500,000", "2,000,000"]
        
        for i, amount in enumerate(amounts):
            btn = QPushButton(amount)
            btn.setFont(QFont("B-nazanin", 14))
            btn.clicked.connect(lambda _, amt=amount: self.process_withdrawal(amt))
            row = i // 2
            col = i % 2
            layout.addWidget(btn, row + 1, col)
        
        custom_btn = QPushButton(self.lang.get_text("custom_amount"))
        custom_btn.setFont(QFont("B-nazanin", 14))
        custom_btn.clicked.connect(self.request_custom_amount)
        
        back_btn = QPushButton(self.lang.get_text("back"))
        back_btn.setFont(QFont("B-nazanin", 14))
        back_btn.clicked.connect(self.back_requested.emit)
        
        layout.addWidget(label, 0, 0, 1, 2)
        layout.addWidget(custom_btn, 3, 0, 1, 2)
        layout.addWidget(back_btn, 4, 0, 1, 2)
        
        self.setLayout(layout)
    
    def process_withdrawal(self, amount_str: str):
        amount = int(amount_str.replace(",", ""))
        if self.bank.withdraw(amount):
            message = (
                f"برداشت وجه با موفقیت انجام شد\nمبلغ: {amount_str}\nموجودی جدید: {self.bank.get_balance():,}"
                if self.lang.get_current_language() == LanguageManager.PERSIAN
                else f"Withdrawal successful\nAmount: {amount_str}\nNew balance: {self.bank.get_balance():,}"
            )
            self.operation_completed.emit(message)
        else:
            self.show_message("Error", self.lang.get_text("insufficient_balance"))
    
    def request_custom_amount(self):
        title = self.lang.get_text("custom_amount")
        prompt = self.lang.get_text("enter_amount")
        
        amount, ok = QInputDialog.getInt(
            self, title, prompt,
            min=10000, max=10000000, step=10000
        )
        
        if ok:
            if self.bank.withdraw(amount):
                amount_str = f"{amount:,}"
                message = (
                    f"برداشت وجه با موفقیت انجام شد\nمبلغ: {amount_str}\nموجودی جدید: {self.bank.get_balance():,}"
                    if self.lang.get_current_language() == LanguageManager.PERSIAN
                    else f"Withdrawal successful\nAmount: {amount_str}\nNew balance: {self.bank.get_balance():,}"
                )
                self.operation_completed.emit(message)
            else:
                self.show_message("Error", self.lang.get_text("insufficient_balance"))


class TransferPage(BasePage):
    def __init__(self, language_manager: LanguageManager, bank_service: BankService):
        self.bank = bank_service
        super().__init__(language_manager)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        amount_label = QLabel(self.lang.get_text("enter_amount"))
        amount_label.setFont(QFont("B-nazanin", 14))
        
        self.amount_input = QLineEdit()
        self.amount_input.setFont(QFont("B-nazanin", 14))
        self.amount_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        card_label = QLabel(self.lang.get_text("enter_dest_card"))
        card_label.setFont(QFont("B-nazanin", 14))
        
        self.card_input = QLineEdit()
        self.card_input.setFont(QFont("B-nazanin", 14))
        self.card_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        confirm_btn = QPushButton(self.lang.get_text("confirm"))
        confirm_btn.setFont(QFont("B-nazanin", 14))
        confirm_btn.clicked.connect(self.process_transfer)
        
        back_btn = QPushButton(self.lang.get_text("back"))
        back_btn.setFont(QFont("B-nazanin", 14))
        back_btn.clicked.connect(self.back_requested.emit)
        
        layout.addWidget(amount_label)
        layout.addWidget(self.amount_input)
        layout.addWidget(card_label)
        layout.addWidget(self.card_input)
        layout.addWidget(confirm_btn)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def process_transfer(self):
        try:
            amount = int(self.amount_input.text())
            dest_card = self.card_input.text()
            
            if self.bank.transfer(amount, dest_card):
                amount_str = f"{amount:,}"
                message = (
                    f"انتقال وجه با موفقیت انجام شد\nمبلغ: {amount_str}\nبه کارت: {dest_card}\nموجودی جدید: {self.bank.get_balance():,}"
                    if self.lang.get_current_language() == LanguageManager.PERSIAN
                    else f"Transfer successful\nAmount: {amount_str}\nTo card: {dest_card}\nNew balance: {self.bank.get_balance():,}"
                )
                self.operation_completed.emit(message)
                self.amount_input.clear()
                self.card_input.clear()
            else:
                if amount <= 0:
                    self.show_message("Error", self.lang.get_text("invalid_amount"))
                elif  not dest_card.isdigit():
                    self.show_message("Error", self.lang.get_text("invalid_card"))
                else:
                    self.show_message("Error", self.lang.get_text("insufficient_balance"))
        except ValueError:
            self.show_message("Error", self.lang.get_text("invalid_amount"))


class BalancePage(BasePage):
    def __init__(self, language_manager: LanguageManager, bank_service: BankService):
        self.bank = bank_service
        super().__init__(language_manager)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.balance_label = QLabel()
        self.balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.balance_label.setFont(QFont("B-nazanin", 20))
        self.update_balance()
        
        back_btn = QPushButton(self.lang.get_text("back"))
        back_btn.setFont(QFont("B-nazanin", 14))
        back_btn.clicked.connect(self.back_requested.emit)
        
        layout.addWidget(self.balance_label)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def update_balance(self):
        balance = self.bank.get_balance()
        self.balance_label.setText(
            f"{self.lang.get_text('your_balance')} {balance:,}"
        )


class ChangePasswordPage(BasePage):
    def __init__(self, language_manager: LanguageManager, bank_service: BankService):
        self.bank = bank_service
        super().__init__(language_manager)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        current_pass_label = QLabel(self.lang.get_text("current_password"))
        current_pass_label.setFont(QFont("B-nazanin", 14))
        
        self.current_pass_input = QLineEdit()
        self.current_pass_input.setFont(QFont("B-nazanin", 14))
        self.current_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.current_pass_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        new_pass_label = QLabel(self.lang.get_text("new_password"))
        new_pass_label.setFont(QFont("B-nazanin", 14))
        
        self.new_pass_input = QLineEdit()
        self.new_pass_input.setFont(QFont("B-nazanin", 14))
        self.new_pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_pass_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        confirm_btn = QPushButton(self.lang.get_text("confirm"))
        confirm_btn.setFont(QFont("B-nazanin", 14))
        confirm_btn.clicked.connect(self.change_password)
        
        back_btn = QPushButton(self.lang.get_text("back"))
        back_btn.setFont(QFont("B-nazanin", 14))
        back_btn.clicked.connect(self.back_requested.emit)
        
        layout.addWidget(current_pass_label)
        layout.addWidget(self.current_pass_input)
        layout.addWidget(new_pass_label)
        layout.addWidget(self.new_pass_input)
        layout.addWidget(confirm_btn)
        layout.addWidget(back_btn)
        
        self.setLayout(layout)
    
    def change_password(self):
        current_pass = self.current_pass_input.text()
        new_pass = self.new_pass_input.text()
        
        if self.bank.change_password(current_pass, new_pass):
            self.operation_completed.emit(self.lang.get_text("password_changed"))
            self.current_pass_input.clear()
            self.new_pass_input.clear()
        else:
            self.show_message("Error", self.lang.get_text("password_change_failed"))


class ResultPage(BasePage):
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.result_label = QLabel()
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setFont(QFont("B-nazanin", 16))
        self.result_label.setWordWrap(True)
        
        new_op_btn = QPushButton(self.lang.get_text("new_operation"))
        new_op_btn.setFont(QFont("B-nazanin", 14))
        new_op_btn.clicked.connect(lambda: self.operation_completed.emit("new_operation"))
        
        exit_btn = QPushButton(self.lang.get_text("exit"))
        exit_btn.setFont(QFont("B-nazanin", 14))
        exit_btn.clicked.connect(lambda: self.operation_completed.emit("exit"))
        
        layout.addWidget(self.result_label)
        layout.addWidget(new_op_btn)
        layout.addWidget(exit_btn)
        
        self.setLayout(layout)
    
    def set_result(self, message: str):
        self.result_label.setText(message)


# -------- main-class ----------
class ATMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        #load users
        self.users = User.load_users('users.csv')

        self.bank = BankService(self.users)
        self.lang = LanguageManager()
        
        self.setWindowTitle("ATM machine")
        self.setFixedSize(800, 600)
        
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)
        
        self.create_pages()
        self.connect_signals()
        
        self.stacked_widget.setCurrentIndex(0)
    
    def create_pages(self):
        self.pages = {
            "language": LanguageSelectionPage(self.lang),
            "login": LoginPage(self.lang, self.bank),
            "menu": MenuPage(self.lang),
            "withdraw": WithdrawPage(self.lang, self.bank),
            "transfer": TransferPage(self.lang, self.bank),
            "balance": BalancePage(self.lang, self.bank),
            "change_password": ChangePasswordPage(self.lang, self.bank),
            "result": ResultPage(self.lang)
        }
        
        for page in self.pages.values():
            self.stacked_widget.addWidget(page)
    
    def connect_signals(self):
        self.pages["language"].operation_completed.connect(self.handle_language)
        
        self.pages["login"].operation_completed.connect(
            lambda: self.stacked_widget.setCurrentWidget(self.pages["menu"])
        )
        
        self.pages["menu"].operation_completed.connect(self.handle_menu_selection)
        
        for page_name in ["withdraw", "transfer", "balance", "change_password"]:
            self.pages[page_name].back_requested.connect(
                lambda: self.stacked_widget.setCurrentWidget(self.pages["menu"])
            )
        
        self.pages["withdraw"].operation_completed.connect(
            lambda msg: self.show_result(msg)
        )
        
        self.pages["transfer"].operation_completed.connect(
            lambda msg: self.show_result(msg)
        )
        
        self.pages["change_password"].operation_completed.connect(
            lambda msg: self.show_result(msg)
        )
        
        self.pages["result"].operation_completed.connect(self.handle_result_action)
    
    def handle_menu_selection(self, action: str):
        if action == "withdraw":
            self.stacked_widget.setCurrentWidget(self.pages["withdraw"])
        elif action == "transfer":
            self.stacked_widget.setCurrentWidget(self.pages["transfer"])
        elif action == "balance":
            self.pages["balance"].update_balance()
            self.stacked_widget.setCurrentWidget(self.pages["balance"])
        elif action == "change_password":
            self.stacked_widget.setCurrentWidget(self.pages["change_password"])
        elif action == "exit":
            self.stacked_widget.setCurrentWidget(self.pages["language"])
    
    def show_result(self, message: str):
        self.pages["result"].set_result(message)
        self.stacked_widget.setCurrentWidget(self.pages["result"])
    
    def handle_result_action(self, action: str):
        if action == "new_operation":
            self.stacked_widget.setCurrentWidget(self.pages["menu"])
        elif action == "exit":
            User.save('users.csv', self.users)
            self.stacked_widget.setCurrentWidget(self.pages["language"])

    def handle_language(self, language):
        self.lang.current_language = language
        self.create_pages()
        self.connect_signals()
        self.stacked_widget.setCurrentWidget(self.pages["login"])


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    
    font = QFont("B-nazanin", 12)
    app.setFont(font)
    
    window = ATMApp()
    window.show()
    sys.exit(app.exec())