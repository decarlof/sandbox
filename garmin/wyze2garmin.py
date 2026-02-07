#!/usr/local/bin/python3
import os
import csv
from wyze_sdk import Client
from wyze_sdk.errors import WyzeApiError
from dotenv import load_dotenv
from datetime import datetime
from requests.exceptions import HTTPError

# Load .env
load_dotenv()

WYZE_EMAIL = os.environ.get('WYZE_EMAIL')
WYZE_PASSWORD = os.environ.get('WYZE_PASSWORD')
WYZE_KEY_ID = os.environ.get('WYZE_KEY_ID')
WYZE_API_KEY = os.environ.get('WYZE_API_KEY')

def login_to_wyze():
    try:
        response = Client().login(
            email=WYZE_EMAIL,
            password=WYZE_PASSWORD,
            key_id=WYZE_KEY_ID,
            api_key=WYZE_API_KEY,
        )
        return response.get("access_token")

    except HTTPError as e:
        # Wyze returns HTTP 400 when 2FA is enabled but no TOTP is provided
        if e.response is not None and e.response.status_code == 400:
            print(
                "\n❌ Wyze login failed (HTTP 400).\n"
                "This often happens when Two-Factor Authentication (2FA) is enabled.\n\n"
                "➡️ Please check the Wyze mobile app:\n"
                "   Account → Security → Two-Factor Authentication\n\n"
                "If 2FA is enabled, either:\n"
                "  • disable it, or\n"
                "  • update this script to provide a TOTP secret to Client(totp_key=...).\n"
            )
        else:
            print(f"HTTP error during Wyze login: {e}")

        return None

    except WyzeApiError as e:
        print(f"Wyze API Error: {e}")
        return None

    except Exception as e:
        print(f"Unexpected error during Wyze login: {e}")
        return None


def export_scale_to_csv(client, scale, csv_file="wyze_scale_data.csv"):
    """Export all records of the scale to CSV"""
    start_ts = int(datetime(2000, 1, 1).timestamp() * 1000)  # get all records
    records = client.scales.get_records(device_mac=scale.mac, start_time=start_ts)
    
    if not records:
        print(f"No records found for scale '{scale.nickname}'")
        return

    headers = [
        "timestamp", "datetime", "weight_kg", "body_fat_pct",
        "body_water_pct", "muscle_mass_kg", "bone_mass_kg",
        "bmr", "bmi", "metabolic_age", "visceral_fat"
    ]

    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for rec in records:
            writer.writerow({
                "timestamp": rec.measure_ts,
                "datetime": datetime.fromtimestamp(rec.measure_ts / 1000).isoformat(),
                "weight_kg": rec.weight * 0.45359237,
                "body_fat_pct": rec.body_fat,
                "body_water_pct": rec.body_water,
                "muscle_mass_kg": rec.muscle,
                "bone_mass_kg": rec.bone_mineral,
                "bmr": rec.bmr,
                "bmi": rec.bmi,
                "metabolic_age": rec.metabolic_age,
                "visceral_fat": rec.body_vfr
            })
    print(f"CSV file generated: {csv_file}")

def export_scale_to_garmin_csv(csv_file, garmin_csv_file):
    """Generate Garmin-compatible CSV with only Date and Weight (plus BMI and Fat as 0)"""
    with open(csv_file, "r", encoding="utf-8") as f_in, \
         open(garmin_csv_file, "w", newline="", encoding="utf-8") as f_out:

        reader = csv.DictReader(f_in)

        # First line required by Garmin
        f_out.write("Body\n")

        # Header line required by Garmin
        headers = ["Date", "Weight", "BMI", "Fat"]
        writer = csv.DictWriter(f_out, fieldnames=headers)
        writer.writeheader()

        for row in reader:
            dt = datetime.fromisoformat(row["datetime"])
            writer.writerow({
                "Date": dt.strftime("%Y-%m-%d"),
                "Weight": round(float(row["weight_kg"]), 2),
                "BMI": 0,
                "Fat": 0
            })

    print(f"Garmin-compatible CSV generated: {garmin_csv_file}")

def main():

    full_csv_file = "bilancia_all.csv"
    garmin_csv_file = "bilancia_garmin.csv"

    access_token = login_to_wyze()
    if not access_token:
        print("Failed to login to Wyze.")
        return

    client = Client(token=access_token)
    for device in client.devices_list():
        if device.nickname == "Bilancia":
            print(f"Exporting scale '{device.nickname}' ({device.mac}) to full CSV...")
            export_scale_to_csv(client, device, csv_file=full_csv_file)
            export_scale_to_garmin_csv(full_csv_file, garmin_csv_file)
            print("Done.")


if __name__ == "__main__":
    main()
