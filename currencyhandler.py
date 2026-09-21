from typing import Any
import requests
import json
import os
from datetime import datetime, timedelta


class CurrencyHandler:
    def __init__(self, base_currency: str = "usd"):
        self.base_currency = base_currency.upper()
        self.currency_data = self.load_currency_data()

    def fetch_currency_data(self) -> dict[str, Any]:
        """
        Fetch the latest currency exchange rate data.
        """
        app_id = "60733892058f44a0b94d9e44c89e1b7b"

        url = f"https://openexchangerates.org/api/latest.json?app_id={app_id}"
        headers = {"accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()
            self.currency_data = data

            self.export_to_json()

            return data

        except requests.RequestException as error:
            print(f"Could not fetch currency data: {error}")
            return {}

    def convert_from_usd(self, to_currency: str, amount: float) -> float:
        """
        Convert an amount from USD to another currency.
        """
        to_currency = to_currency.upper()

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        if to_currency not in self.currency_data["rates"]:
            raise ValueError("Invalid currency code.")

        rate = self.currency_data["rates"][to_currency]

        return amount * rate

    def convert_any_currency(
        self, from_currency: str, to_currency: str, amount: float
    ) -> float:
        """
        Convert an amount from one currency to another.
        """
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()

        if amount < 0:
            raise ValueError("Amount cannot be negative.")

        rates = self.currency_data["rates"]

        if from_currency != "USD" and from_currency not in rates:
            raise ValueError("Invalid source currency.")

        if to_currency != "USD" and to_currency not in rates:
            raise ValueError("Invalid target currency.")

        if from_currency == "USD":
            usd_amount = amount
        else:
            usd_amount = amount / rates[from_currency]

        if to_currency == "USD":
            return usd_amount

        return usd_amount * rates[to_currency]

    def list_currencies(self) -> list[str]:
        """
        List all available currencies in alphabetical order.
        """
        currencies = list(self.currency_data["rates"].keys())
        currencies.append("USD")

        return sorted(currencies)

    def load_currency_data(self) -> dict[str, Any]:
        """
        Load currency data from a JSON file.
        """
        filename = "currency_data.json"

        if not os.path.exists(filename):
            return self.fetch_currency_data()

        try:
            with open(filename, "r") as file:
                data = json.load(file)

            saved_time = data["saved_at"]
            current_time = datetime.now().timestamp()

            # Update the data if it is more than one hour old.
            if current_time - saved_time > 3600:
                return self.fetch_currency_data()

            return data["currency_data"]

        except (OSError, KeyError, json.JSONDecodeError):
            return self.fetch_currency_data()

    def export_to_json(self) -> None:
        """
        Save the current currency data to a JSON file.
        """
        data = {
            "saved_at": datetime.now().timestamp(),
            "currency_data": self.currency_data
        }

        try:
            with open("currency_data.json", "w") as file:
                json.dump(data, file, indent=4)

        except OSError as error:
            raise IOError(f"Could not save currency data: {error}")

    def get_historical_rate(
        self, date: str, base_currency: str
    ) -> dict[str, Any]:
        """
        Get historical exchange rates for a specific date.
        """
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format.")

        base_currency = base_currency.upper()

        app_id = "60733892058f44a0b94d9e44c89e1b7b"

        url = (
            f"https://openexchangerates.org/api/historical/"
            f"{date}.json?app_id={app_id}"
        )

        headers = {"accept": "application/json"}

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

        except requests.RequestException as error:
            raise RuntimeError(
                f"Could not fetch historical data: {error}"
            )

        if base_currency == "USD":
            return data

        if base_currency not in data["rates"]:
            raise ValueError("Invalid currency code.")

        base_rate = data["rates"][base_currency]
        new_rates = {}

        for currency, rate in data["rates"].items():
            new_rates[currency] = rate / base_rate

        new_rates["USD"] = 1 / base_rate

        return {
            "timestamp": data["timestamp"],
            "base": base_currency,
            "rates": new_rates
        }

    def list_historical_rates_for_currency(
        self, currency: str, days: int
    ) -> list[tuple[str, str]]:
        """
        Get exchange rates for a currency over several days.
        """
        currency = currency.upper()

        if days <= 0:
            raise ValueError("Days must be greater than 0.")

        if currency != "USD" and currency not in self.currency_data["rates"]:
            raise ValueError("Invalid currency code.")

        historical_rates = []

        for i in range(days):
            date = (
                datetime.now() - timedelta(days=i + 1)
            ).strftime("%Y-%m-%d")

            try:
                data = self.get_historical_rate(date, "USD")

                if currency == "USD":
                    rate = 1
                else:
                    rate = data["rates"].get(currency)

                if rate is not None:
                    historical_rates.append(
                        (date, str(rate))
                    )

            except RuntimeError:
                print(f"Could not get data for {date}.")

        historical_rates.reverse()

        return historical_rates