"""
Command-line interface of Symi
"""
from SymiInstance import SymiInstance, bcolors
import traceback


def main():
    """
    Symi main function
    """
    symi = SymiInstance()
    while 1:
        try:
            line = input(symi.PS1)
            if symi.parse_line(line) == 0:
                break
        except KeyboardInterrupt:
            symi.exit()
            break
        except Exception:
            print(bcolors.FAIL)
            traceback.print_exc()
            print(bcolors.ENDC)


if __name__ == "__main__":
    main()