from functools import wraps
from address_book import AddressBook, Record, FieldValueError


def main():
    book = AddressBook()
    book.load_data()
    print("Welcome to the assistant bot!")

    while True:
        try:
            user_input = input("Enter a command: ")
        except KeyboardInterrupt:
            print("exit")
            command = "exit"
        else:
            command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(show_upcoming_birthdays(book))
        else:
            print("Invalid command.")

    book.save_data()


def parse_input(user_input):
    input_list = user_input.split()
    if not input_list:
        return [""]  # Return an empty command if no input is provided
    cmd = input_list[0].strip().lower()
    args = input_list[1:]
    return cmd, *args


def input_error(func):
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me arguments please."
        except FieldValueError as e:
            return str(e)

    return inner


@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        record = Record(name)
        message = "Contact added."
    else:
        message = "Contact updated."
    record.add_phone(phone)
    book.add_record(record)
    return message


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.edit_phone(old_phone, new_phone)
    return "Contact changed."


@input_error
def show_phone(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return record.show_phones()


def show_all(book):
    return book


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    return record.show_birthday()


def show_upcoming_birthdays(book):
    return book.get_upcoming_birthdays()


if __name__ == "__main__":
    main()
