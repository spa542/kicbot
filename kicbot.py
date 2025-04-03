import os
import pickle
import base64
import click
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


# The 'credentials.json' file you downloaded from the Google Cloud Console
CLIENT_SECRET_FILE = 'credentials.json'
# The API you want to access (Gmail API example)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']


def authenticate_gmail(local):
    """Authenticate the app using OAuth 2.0 and get the Gmail API service."""
    creds = None

    # Check if we have a token.pickle file (saved credentials from previous authentication)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    elif local and not os.path.exists('credentials.json'):
        # Check and make sure credentials.json is present
        raise Exception('Please save credentials.json for OAuth2.0 testing locally in cwd')

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Perform OAuth 2.0 flow (this will open a browser window)
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=8888)  # This will open a local server for the flow

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the Gmail API service
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None


def list_gmail_messages(service):
    """List Gmail messages (example use of Gmail API)."""

    if service:
        try:
            results = service.users().messages().list(userId='me', labelIds=['INBOX'], q="is:unread").execute()
            messages = results.get('messages', [])

            if not messages:
                print('No unread messages.')
            else:
                print('Unread messages:')
                for message in messages:
                    msg = service.users().messages().get(userId='me', id=message['id']).execute()
                    print(f"Message snippet: {msg['snippet']}")
        except HttpError as error:
            print(f'An error occurred: {error}')


def create_message(sender, to, subject, body):
    """Create a message for the email."""
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(body)
    message.attach(msg)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def send_email(service, sender, to, subject, body):
    """Send an email via the Gmail API."""
    try:
        message = create_message(sender, to, subject, body)
        send_message = service.users().messages().send(userId="me", body=message).execute()
        print(f"Message sent successfully! Message ID: {send_message['id']}")
    except Exception as error:
        print(f"An error occurred: {error}")


@click.command()
@click.option('--local', is_flag=True, help='Run for local testing (default is Lambda).')
@click.argument('operation', type=click.Choice(['list', 'send'], case_sensitive=False), default='send', required=True)
@click.argument('email', type=str, required=False)
@click.argument('subject', type=str, required=False)
@click.argument('body', type=str, required=False)
def main(local, operation, email, subject, body):
    # Arg validation
    if not local:
        print("Running in Lambda environment (Stub) - No action performed.")
        # Lambda-specific code would be added here in the future.
        return

    # Local Testing: Ensure we have the necessary arguments based on the operation
    if operation == 'send':
        if not email or not subject or not body:
            raise click.BadParameter("For 'send' operation, 'email', 'subject', and 'body' are required.")
    elif operation == 'list':
        # No additional arguments required for list operation
        pass

    # Authenticate and build the Gmail API service
    service = authenticate_gmail(local)

    # Perform the requested operation
    if operation == 'send':
        # Will send a test email to self
        sender = email
        recipient = email
        send_email(service, sender, recipient, subject, body)
    elif operation == 'list':
        list_gmail_messages(service)


if __name__ == '__main__':
    main()
