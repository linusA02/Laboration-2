from typing import Any

import requests
from currencyhandler import CurrencyHandler


def main() -> None:
    """
    The main function that runs the currency conversion application.
    """

    currency_handler = CurrencyHandler()

    while True:
        print("\nCurrency Converter Menu:")
        print("[0] - List all currencies")
        print("[1] - Convert USD to a currency of choice")
        print("[2] - Refresh the data (fetch new currency data)")
        print("[3] - Export the data to JSON")
        print("[4] - Convert from any currency to any currency")
        print("[5] - Get historical exchange rate")
        print("[6] - Get rate trend for a currency")
        print("[7] - Exit the application")

        choice = input("Enter your choice (0-7): ")

        if choice == "0":
            currencies = currency_handler.list_currencies()

            print("\nAvailable currencies:")
            print(", ".join(currencies))

        elif choice == "1":
            try:
                currency = input("Enter the currency you want to convert to: ")
                amount = float(input("Enter the amount in USD: "))

                result = currency_handler.convert_from_usd(currency, amount)

                print(f"{amount:.2f} USD = {result:.2f} {currency.upper()}")

            except ValueError as error:
                print(f"Error: {error}")

        elif choice == "2":
            data = currency_handler.fetch_currency_data()

            if data:
                print("Currency data has been refreshed.")
            else:
                print("Could not refresh currency data.")

        elif choice == "3":
            try:
                currency_handler.export_to_json()
                print("Currency data has been exported to JSON.")

            except IOError as error:
                print(f"Error: {error}")

        elif choice == "4":
            try:
                from_currency = input("Enter the currency you have: ")
                to_currency = input("Enter the currency you want: ")
                amount = float(input("Enter the amount: "))

                result = currency_handler.convert_any_currency(
                    from_currency,
                    to_currency,
                    amount
                )

                print(
                    f"{amount:.2f} {from_currency.upper()} = "
                    f"{result:.2f} {to_currency.upper()}"
                )

            except ValueError as error:
                print(f"Error: {error}")

        elif choice == "5":
            try:
                date = input("Enter date (YYYY-MM-DD): ")
                base_currency = input("Enter base currency: ")

                data = currency_handler.get_historical_rate(
                    date,
                    base_currency
                )

                print(f"\nHistorical rates for {date}")
                print(f"Base currency: {data['base']}")

                for currency, rate in data["rates"].items():
                    print(f"{currency}: {rate}")

            except (ValueError, RuntimeError) as error:
                print(f"Error: {error}")

        elif choice == "6":
            try:
                currency = input("Enter currency: ")
                days = int(input("How many days do you want to check? "))

                rates = currency_handler.list_historical_rates_for_currency(
                    currency,
                    days
                )

                print(f"\nHistorical rates for {currency.upper()}:")

                for date, rate in rates:
                    print(f"{date}: {rate}")

            except ValueError as error:
                print(f"Error: {error}")

        elif choice == "7":
            print("Thank you for using the Currency Converter. Goodbye!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()