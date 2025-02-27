from hanzi_ceshi.data_types import load_character_list
from hanzi_ceshi.tester import SimpleTester


def main():
    tester = SimpleTester(load_character_list(), bin_size=500)

    test = tester.characters()
    for char in test:
        print(char)
        answer = input("Do you know this? (y/n): ") == "y"
        try:
            test.send(answer)
        except StopIteration:
            pass

    tester.print_debug_info()
    count = tester.estimate_count()
    print(f"You know an estimated {count} characters")


if __name__ == "__main__":
    main()
