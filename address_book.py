from collections import UserDict
from datetime import datetime
import pickle


class Field:
    def __init__(self, value):
        self._validate(value)
        self.__value = value

    def __str__(self):
        return str(self.__value)

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self._validate(value)
        self.__value = value

    def _validate(self, value):
        if not value:
            raise FieldValueError("Field value cannot be empty.")


class Name(Field):
    # реалізація класу
    pass


class Phone(Field):
    # Format is 10 digits, only numbers allowed
    def _validate(self, value):
        if not value or not value.isdigit() or len(value) != 10:
            raise FieldValueError(
                f"Phone number {value} is not valid. "
                f"Phone number must be 10 digits long "
                f"and contain only numbers.")


class Birthday(Field):
    # Format is DD.MM.YYYY
    DATETIME_FORMAT = "%d.%m.%Y"
    DESC_FORMAT = "DD.MM.YYYY"

    def _validate(self, value):
        try:
            datetime.strptime(value, Birthday.DATETIME_FORMAT)
        except ValueError:
            raise FieldValueError(
                f"Date {value} is not valid. "
                f"Birthday must be in {Birthday.DESC_FORMAT} format.")

    def __date(self) -> datetime:
        return datetime.strptime(self.value, Birthday.DATETIME_FORMAT).date()

    def __upcoming_birthday(self) -> datetime:
        today = datetime.today().date()
        birthday_this_year = self.__date().replace(year=today.year)
        if birthday_this_year < today:
            return birthday_this_year.replace(year=today.year + 1)
        else:
            return birthday_this_year

    # Method returns the date for congratulation, which is the birthday date
    # if it falls on a weekday, or the next Monday if it falls on a weekend.
    # If the birthday is more than 7 days away, returns None.
    def congratulation_date(self) -> str | None:
        today = datetime.today().date()
        # more than 7 days starting from today
        date = self.__upcoming_birthday()
        if (date - today).days >= 7:
            return None

        birthday_weekday = date.weekday()
        weekend_cnt = 0
        if birthday_weekday == 5:  # Saturday
            weekend_cnt = 2
        elif birthday_weekday == 6:  # Sunday
            weekend_cnt = 1
        date = date.replace(day=date.day + weekend_cnt)

        return date.strftime(Birthday.DATETIME_FORMAT)


class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.__birthday: Birthday | None = None

    @property
    def birthday(self):
        return self.__birthday if self.__birthday else "not specified"

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        for p in self.phones:
            if p.value == old_phone:
                p.value = new_phone
                return
        raise FieldValueError(f"Phone {old_phone} not found")

    def find_phone(self, phone: str) -> Phone | None:
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def remove_phone(self, phone: str):
        phone_obj = self.find_phone(phone)
        if phone_obj is not None:
            self.phones.remove(phone_obj)

    def add_birthday(self, birthday: str):
        self.__birthday = Birthday(birthday)

    def congratulation_date(self) -> dict | None:
        if self.__birthday is None:
            return None
        congratulation_date = self.__birthday.congratulation_date()
        if congratulation_date is None:
            return None
        return {
            "name": self.name.value,
            "congratulation_date": congratulation_date
        }

    def __show_name(self) -> str:
        return f"Contact name: {self.name.value}"

    def __show_birthday(self) -> str:
        return f"birthday: {self.birthday}"

    def __show_phones(self) -> str:
        return f"phones: {'; '.join(p.value for p in self.phones)}"

    def show_birthday(self) -> str:
        return f"{self.__show_name()}, {self.__show_birthday()}"

    def show_phones(self) -> str:
        return f"{self.__show_name()}, {self.__show_phones()}"

    def __str__(self):
        return f"{self.__show_name()}, " \
               f"{self.__show_birthday()}, " \
               f"{self.__show_phones()}"


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str) -> Record | None:
        return self.data.get(name)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self) -> list:
        res = "Upcoming birthdays:\n"

        for record in self.data.values():
            date = record.congratulation_date()
            if date is None:
                continue
            res += f"{date['name']}: {date['congratulation_date']}\n"

        return res

    def save_data(self, filename: str = "addressbook.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.data, f)
    
    def load_data(self, filename: str = "addressbook.pkl"):
        try:
            with open(filename, "rb") as f:
                self.data = pickle.load(f)
        except FileNotFoundError:
            self.data = {}

    def __str__(self):
        res = "Address Book:\n"
        for record in self.data.values():
            res = res + str(record) + "\n"
        return res


class FieldValueError(Exception):
    default_message = "Field Value does not meet validation criteria."

    def __init__(self, message=default_message):
        super().__init__(message)
