import argparse
from lakeshore350.idn import print_idn
from lakeshore350.read_temps import read_temperatures
from lakeshore350.set_heater import set_heater_range


def main():
    parser = argparse.ArgumentParser(
        description="Lake Shore 350 Python Driver CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # IDN command
    parser_idn = subparsers.add_parser("idn", help="Query device identification")

    # Read temps
    parser_temps = subparsers.add_parser("read-temps", help="Read all temperature inputs")

    # Set heater
    parser_heater = subparsers.add_parser("set-heater", help="Set heater loop range")
    parser_heater.add_argument("--loop", type=int, required=True, help="Heater loop number (1-4)")
    parser_heater.add_argument("--range", type=int, required=True, help="Heater output range (0=off, 1=low, 2=med, 3=high)")

    args = parser.parse_args()

    if args.command == "idn":
        print_idn()

    elif args.command == "read-temps":
        read_temperatures()

    elif args.command == "set-heater":
        set_heater_range(args.loop, args.range)


if __name__ == "__main__":
    main()
