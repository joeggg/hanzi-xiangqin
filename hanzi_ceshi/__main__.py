from hanzi_ceshi.data_types import load_character_list
from hanzi_ceshi.tester import SimpleTester


def main():
    tester = SimpleTester(load_character_list(), bin_size=500)

    test = tester.characters()
    for char in test:
        print(char)
        answer = input("Correct? (y/n): ") == "y"
        test.send(answer)

    count = test.close()
    print(f"You know an estimated {count} characters")


if __name__ == "__main__":
    main()
