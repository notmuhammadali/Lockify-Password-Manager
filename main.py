from tkinter import *
from tkinter import messagebox
from cryptography.fernet import Fernet
import random
import pandas
import pandastable
import ctypes as ct
import playsoundsimple

LETTERS_LOWER = 'a b c d e f g h i j k l m n o p q r s t u v w x y z'.split()
LETTERS_UPPER = 'A B C D E F G H I J K L M N O P Q R S T U V W X Y Z'.split()
NUMBERS = '0 1 2 3 4 5 6 7 8 9'.split()
SYMBOLS = '! ? @ # : & * % $ ^'.split()

BG_COLOR = "#B0BEC5"
BUTTON_COLOR = "#00ACC1"
FONT = "Gill Sans MT Bold"

ui_click = playsoundsimple.Sound("ui-click.mp3")


# ---------------------------- PASSWORD GENERATOR ------------------------------- #

def generate_password():
    ui_click.play()
    nr_letters_lower = 4
    nr_letters_upper = 4
    nr_numbers = 5
    nr_symbols = 4

    password_letters_lower = [random.choice(LETTERS_LOWER) for _ in range(nr_letters_lower)]
    password_letters_upper = [random.choice(LETTERS_UPPER) for _ in range(nr_letters_upper)]
    password_numbers = [random.choice(NUMBERS) for _ in range(nr_numbers)]
    password_symbols = [random.choice(SYMBOLS) for _ in range(nr_symbols)]

    password_list = password_letters_lower + password_letters_upper + password_symbols + password_numbers
    random.shuffle(password_list)
    password = ''.join(password_list)

    password_entry.delete(0, END)
    password_entry.insert(0, password)
    window.clipboard_clear()
    window.clipboard_append(password)


# ---------------------------- ENCRYPTION & DECRYPTION ------------------------------- #


def decrypt_dataframe():
    # Read the encrypted data from the CSV file
    df = pandas.read_csv("data.csv")

    # opening the key
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()

    # using the generated key
    fernet = Fernet(key)

    # Decrypt the data
    df['Website'] = df['Website'].apply(lambda x: fernet.decrypt(str(x)).decode())
    df['Email'] = df['Email'].apply(lambda x: fernet.decrypt(str(x)).decode())
    df['Password'] = df['Password'].apply(lambda x: fernet.decrypt(str(x)).decode())

    # Return the decrypted DataFrame
    return df


# Button event handler
def show_decrypted_data():
    ui_click.play()
    # Decrypts the data and gets the decrypted DataFrame
    decrypted_df = decrypt_dataframe()

    data_window = Toplevel(window)
    data_window.title("Confidential!")
    dark_title_bar(data_window)
    table = pandastable.Table(data_window, dataframe=decrypted_df)
    options = {'fontsize': 10, 'cellbackgr': BG_COLOR, 'textcolor': "#D21312", 'rowselectedcolor': 'White'}
    pandastable.config.apply_options(options, table)
    table.show()


def encrypt_dataframe(website, email, password):
    # opening the key
    with open('filekey.key', 'rb') as filekey:
        key = filekey.read()

    # using the generated key
    fernet = Fernet(key)

    # Encrypt the data
    enc_website = fernet.encrypt(website.encode()).decode()
    enc_email = fernet.encrypt(email.encode()).decode()
    enc_password = fernet.encrypt(password.encode()).decode()

    # Create a dictionary with encrypted data
    data = {
        "Website": [enc_website],
        "Email": [enc_email],
        "Password": [enc_password]
    }

    # Create a DataFrame
    df = pandas.DataFrame(data)
    # Append the DataFrame to the CSV file
    df.to_csv('data.csv', mode='a', index=False, header=False)


# ---------------------------- SAVE PASSWORD ------------------------------- #


def save_details():
    ui_click.play()
    website = website_entry.get()
    email = email_username_entry.get()
    password = password_entry.get()

    # Check if entry fields are empty
    if len(website) == 0 or len(email) == 0 or len(password) == 0:
        messagebox.showwarning(title='Empty fields', message="Please ensure you haven't left any fields empty")
        return

    # Check with the user to confirm the entry is correct
    confirmed_entry = messagebox.askokcancel(title='Entry confirmation',
                                             message=f'Confirm Details:\nWebsite: {website}\nUsername: {email}\n'
                                                     f'Password: {password}')

    if confirmed_entry:

        encrypt_dataframe(website, email, password)

        # Wipe clear the text in the entry fields
        website_entry.delete(0, 'end')
        password_entry.delete(0, 'end')

    else:  # If the user does not confirm the entry cancel the add
        return


# ---------------------------- UI SETUP ------------------------------- #

def about_window():
    ui_click.play()
    about = Toplevel()
    dark_title_bar(about)
    about.geometry("335x380")
    about.title("About")
    about.config(bg=BG_COLOR)

    about_label = Label(about,
                        text='ABOUT LOCKIFY\n'
                             'Lockify is a secure password manager\n'
                             'designed to keep your sensitive data safe\n'
                             'and easily accessible. With Lockify,\n'
                             'you can store your website credentials\n'
                             'securely, knowing that they are encrypted\n'
                             'using advanced encryption techniques.\n'
                             '\nHOW IT WORKS:\n'
                             'Lockify uses a symmetric encryption\n'
                             'technique to encrypt your data securely.\n'
                             'When you add a new entry,\n'
                             'Lockify encrypts the website, email, and\n'
                             'password using a unique encryption key\n '
                             'stored locally on your device.This encrypted\n'
                             'data is then stored in a CSV file, ensuring\n'
                             'that your information remains safe even if\n'
                             'the file is accessed by unauthorized users.\n',
                        background=BG_COLOR,
                        font=("Bell Gothic Std Black", 12, "italic"))
    about_label.grid(column=0, row=0)

    copyright_label = Label(about,
                            text="© Muhammad Ali.",
                            background=BG_COLOR,
                            font=("Arial", 10, "italic"))
    copyright_label.place(x=215, y=355)


def dark_title_bar(custom):
    """
    MORE INFO: https://learn.microsoft.com/en-us/windows/win32/api/dwmapi/ne-dwmapi-dwmwindowattribute
    """
    custom.update()
    set_window_attribute = ct.windll.dwmapi.DwmSetWindowAttribute
    get_parent = ct.windll.user32.GetParent
    hwnd = get_parent(custom.winfo_id())
    value = 2
    value = ct.c_int(value)
    set_window_attribute(hwnd, 20, ct.byref(value), 4)


window = Tk()
window.title("Lockify")
window.config(padx=10, pady=10, background=BG_COLOR)
dark_title_bar(window)
window.geometry("465x365")

canvas = Canvas(width=200, height=200, background=BG_COLOR, highlightbackground=BG_COLOR)
logo = PhotoImage(file="Lockify.png")
canvas.create_image(120, 90, image=logo)
canvas.grid(column=1, row=0)

# Various Labels
website_label = Label(text="Website:", pady=3,
                      font=(FONT, 10, "bold"),
                      background=BG_COLOR)
website_label.grid(column=0, row=1)

email_username = Label(text="Email/Username:",
                       font=(FONT, 10, "bold"),
                       background=BG_COLOR)
email_username.grid(column=0, row=2)

password_label = Label(text="Password:",
                       font=(FONT, 10, "bold"),
                       background=BG_COLOR)
password_label.grid(column=0, row=3)

# Various Entries
website_entry = Entry(window, width=52)
website_entry.place(x=117, y=205)
website_entry.focus()

email_username_entry = Entry(window, width=52)
email_username_entry.place(x=117, y=230)
email_username_entry.insert(0, "example@gmail.com")

password_entry = Entry(window, width=32)
password_entry.place(x=117, y=255)

# Various Buttons
generate_password_button = Button(text="Generate Password",
                                  font=(FONT, 9, "normal"),
                                  width=16,
                                  command=generate_password,
                                  background=BUTTON_COLOR)
generate_password_button.place(x=312, y=252)

add_button = Button(text="Add",
                    font=(FONT, 9, "normal"),
                    width=44,
                    command=save_details,
                    background=BUTTON_COLOR)
add_button.place(x=117, y=280)

show_password_button = Button(text="Show Passwords",
                              font=(FONT, 9, "normal"),
                              width=44,
                              command=show_decrypted_data,
                              background=BUTTON_COLOR)
show_password_button.place(x=117, y=310)

about_button = Button(text="About",
                      background=BUTTON_COLOR,
                      command=about_window)
about_button.place(x=10, y=10)

window.mainloop()
