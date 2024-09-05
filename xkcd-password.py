#!/usr/bin/python3

# Just run the program 

import argparse
import random
import requests

# function to fetch random words from an online API
def fetch_words(word_count=1000):
    try:
        response = requests.get(f"https://random-word-api.herokuapp.com/word?number={word_count}")
        response.raise_for_status()  # check for request errors
        return response.json()  # return the list of words
    except requests.RequestException as e:
        print(f"Error fetching words from the API: {e}")
        exit(1)

# generate a password
def generate_password(word_count, caps_count, number_count, symbol_count, words):
    password_list = []

    # randomly select words and capitalize some if required
    capital_indices = random.sample(range(word_count), min(caps_count, word_count))
    for i in range(word_count):
        word = random.choice(words)
        if i in capital_indices:
            word = word.capitalize()
        password_list.append(word)

    # insert random numbers
    for _ in range(number_count):
        password_list.insert(random.randint(0, len(password_list)), str(random.randint(0, 9)))

    # insert random symbols
    symbols_list = ["~", "!", "@", "#", "$", "%", "^", "&", "*", ".", ":", ";"]
    for _ in range(symbol_count):
        password_list.insert(random.randint(0, len(password_list)), random.choice(symbols_list))

    # return the final password as a string
    return ''.join(password_list)

def get_user_input(prompt, default_value):
    user_input = input(f"{prompt} (default = {default_value}): ").strip()
    return int(user_input) if user_input else default_value

def main():
    # argument parser setup
    parser = argparse.ArgumentParser(description="Generate a secure password using the XKCD method")

    # commandline arguments for customization
    parser.add_argument('-w', '--words', type=int, help='Include WORDS words in the password (default = 4)')
    parser.add_argument('-c', '--caps', type=int, help='Capitalize the first letter of CAPS random words (default = 0)')
    parser.add_argument('-n', '--numbers', type=int, help='Insert NUMBERS random numbers in the password')
    parser.add_argument('-s', '--symbols', type=int, help='Insert SYMBOLS random symbols in the password (default = 0)')

    # parse the arguments
    args = parser.parse_args()

    # check if arguments were provided; if not, use interactive mode
    if args.words is None and args.caps is None and args.numbers is None and args.symbols is None:
        print("Interactive Mode! \n Just press Enter to use default values.")

        # get user inputs with defaults
        word_count = get_user_input("How many words?", 4)
        caps_count = get_user_input("How many capitalized words?", 0)
        number_count = get_user_input("How many random numbers?", 0)
        symbol_count = get_user_input("How many random symbols?", 0)
    else:
        # use commandline arguments if provided
        word_count = args.words if args.words is not None else 4
        caps_count = args.caps if args.caps is not None else 0
        number_count = args.numbers if args.numbers is not None else 0
        symbol_count = args.symbols if args.symbols is not None else 0

    # fetch random words 
    words = fetch_words()

    # generate the password and print
    password = generate_password(word_count, caps_count, number_count, symbol_count, words)

    print("Generated Password:", password)

if __name__ == "__main__":
    main()
