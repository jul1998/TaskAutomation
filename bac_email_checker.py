import imaplib
import email
import yaml
import pandas as pd
from bs4 import BeautifulSoup
import datetime

from google_sheets import get_values, update_values

# Load config file
def get_credentials():
    with open("credentials.yml") as f:
        credentials = yaml.safe_load(f)

    user, password = credentials["user"], credentials["password"]
    return user, password


def get_mailbox_status(user,password):
    # Connect to the server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    imap.login(user, password)

    # Select the mailbox
    status, messages = imap.select("INBOX")
    key = "FROM"
    value = "notificacion@notificacionesbaccr.com"

    # Search for emails
    status, response = imap.search(None, f"{key} {value}")

    # Get the list of email IDs and reverse the order
    message_ids = response[0].split()[::-1]  # Reverse the list using slicing

    return message_ids, imap


def parse_date_string(date_str):
    # Define a list of possible date formats
    date_formats = ["%b %d, %Y, %H:%M", "%b %d, %Y, %H:%M:%S"]

    for date_format in date_formats:
        try:
            fecha_obj = datetime.datetime.strptime(date_str, date_format)
            return fecha_obj.strftime("%Y-%m-%d")  # Convert to "YYYY-MM-DD" format
        except ValueError:
            continue  # Try the next date format

    # If none of the formats work, handle it as needed
    return date_str.replace("'", "")  # You can return None or another default value

def main():

    user, password = get_credentials()

    message_ids, imap = get_mailbox_status(user, password)

    # Create an empty list to store JSON records
    json_records =[]

    messages_epochs = 100

    for num in message_ids[:messages_epochs]:
        # Fetch the email
        status, response = imap.fetch(num, "(RFC822)")
        # Get the email content
        msg = email.message_from_bytes(response[0][1])

        html_text = ""

        # Iterate through email parts (body and attachments)
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            # Extract HTML content
            if "text/html" in content_type and "attachment" not in content_disposition:
                html_text += part.get_payload(decode=True).decode()

        # Parse the HTML content with BeautifulSoup
        if html_text:
            soup = BeautifulSoup(html_text, "html.parser")
            # Find the table element
            table = soup.find("table")
            if table:
                # Find all table rows
                rows = table.find_all("tr")
                record = {}  # Initialize a new dictionary for each email message
                for row in rows:
                    # Find all table cells (td elements)
                    cells = row.find_all("td")
                    if len(cells) == 2:
                        # Extract the labels and values from the cells
                        label = cells[0].get_text(strip=True)
                        value = cells[1].get_text(strip=True)

                        # Only append non-empty label-value pairs to the dictionary
                        exclude_labels = ['Cookies', 'Seguridad', 'Políticas de privacidad', "Seguridad|Políticas\r\nde\r\nprivacidad|Términos\r\ny condicionesTODOS LOS DERECHOS RESERVADOS.2023 © BAC INTERNATIONAL BANK"]
                        if label.strip() and value.strip() and label not in exclude_labels:
                            if label == 'Monto:':
                                value = float(
                                    value.replace(',', '').replace('$', '').replace('USD', "").replace('CRC', '').strip())
                            elif label == 'Fecha:':
                                fecha_str = parse_date_string(value)
                                if fecha_str:
                                    value = fecha_str
                                else:
                                    # Handle the case where date parsing failed
                                    # You can set a default value or handle it as needed
                                    value = "Unknown Date"
                            record[label] = value  # Append to the current record dictionary

                # Append the current record to the list of records
                json_records.append(record)

    imap.logout()
        # Append the label-value dictionary to the list
        # if label_value_dict:
        #     df_list.append(pd.DataFrame([label_value_dict]))

    # # Concatenate the list of DataFrames into a single DataFrame
    # final_df = pd.concat(df_list, ignore_index=True)
    # # Drop a specific column by its index (e.g., column at index 0)
    # final_df.drop(final_df.columns[-1:-2], axis=1, inplace=True)
    #
    # # Save the DataFrame to a CSV file
    # final_df.to_excel("bac_msgs.xlsx", index=False)

    # print("Connection closed.")
    # # Convert the DataFrame to a list of lists
    # values_to_upload = final_df.values.tolist()
    # print(values_to_upload)
    # Update values in Google Sheets


    spreadsheet_id = "1ryuN-fTpx4Dk1yMMx36GsMiNC-bf2m6O4Ld3UeQooMg"
    range_name = "Sheet1"
    value_input_option = "RAW"

    update_values(spreadsheet_id, range_name, "RAW", json_records)

if __name__ == "__main__":
    main()
