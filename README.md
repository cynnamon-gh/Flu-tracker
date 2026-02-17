# Cold & Flu Tracker

A simple text message service that asks people once a week if they've been sick. Designed to compare illness rates between people who use far-UV lamps and people who don't.

People sign up by texting your number. Every week, the service texts them to ask if they were sick. All the data is stored anonymously so no one's health info can be tied back to their phone number.

---

## What You'll Need

- A credit card (for Twilio - it costs about $1-2/month for the phone number, plus less than a penny per text)
- A Google Cloud account (the server runs for free on Google's free tier)
- A computer (Mac or Windows) for initial setup and viewing data

---

## Step 1: Set Up Twilio (Your Text Message Number)

Twilio is the service that actually sends and receives text messages. Here's how to get set up:

### 1a: Create a Twilio account
1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account (you'll need to verify your email and phone number)
3. When it asks what you want to build, pick anything - it doesn't matter

### 1b: Buy a phone number
1. Once you're logged in, go to https://console.twilio.com/us1/develop/phone-numbers/manage/search
2. Make sure **"US"** is selected as the country (or whichever country you want)
3. Make sure the **"SMS"** checkbox is checked under "Capabilities"
4. Click **"Search"**
5. Pick any number from the list and click **"Buy"** (it costs about $1.15/month)
6. Confirm the purchase

### 1c: Find your credentials
1. Go to https://console.twilio.com (the main dashboard)
2. You'll see two important values right on the dashboard:
   - **Account SID** - starts with "AC" followed by a long string of letters and numbers
   - **Auth Token** - click "Show" to reveal it - another long string
3. Write these down or keep this page open - you'll need them in the next step

---

## Step 4: Configure the Project

1. Open the project folder (the one you unzipped)
2. Find the file called `.env.example`
   - **Note:** On some computers, files starting with a dot are hidden. If you can't see it:
     - **Windows:** In File Explorer, click "View" at the top, then check "Hidden items"
     - **Mac:** In Finder, press Cmd+Shift+. (period)
3. Make a copy of `.env.example` and rename the copy to `.env` (just remove the `.example` part)
4. Open `.env` in any text editor (Notepad is fine!)
5. Fill in your values:

```
TWILIO_ACCOUNT_SID=paste_your_account_sid_here
TWILIO_AUTH_TOKEN=paste_your_auth_token_here
TWILIO_PHONE_NUMBER=+12125551234
```

Replace `+12125551234` with the phone number you bought in Step 3b. Keep the `+1` at the beginning - that's the US country code. No spaces, no dashes, just digits after the +1.

6. For the encryption key, you need to generate one. Open a terminal (see Step 1 for how) and type this, then press Enter:

```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

It will print out a long string of random characters. Copy that entire string and paste it as your `ENCRYPTION_KEY` value in the `.env` file.

7. Save the `.env` file.

---

## Step 5: Install the Required Packages

This only needs to be done once.

1. Open a terminal
2. Navigate to the project folder by typing:
   - **Windows:** `cd Desktop\flu-tracker` (adjust the path if you put it somewhere else)
   - **Mac:** `cd ~/Desktop/flu-tracker`
3. Type this command and press Enter:

```
pip install -r requirements.txt
```

**If you get an error** like "pip is not recognized" or "command not found", try `pip3` instead:
```
pip3 install -r requirements.txt
```

Still not working? Python might not be in your PATH. Go back to Step 1 and reinstall Python, making sure to check that **"Add Python to PATH"** box.

You'll see a bunch of text scroll by as things install. Wait until it finishes (you'll see your cursor come back). If you see "Successfully installed..." at the end, you're good!

---

## Step 6: Deploy to Google Cloud (Ask Cynthia For Help)

The server runs 24/7 on a free Google Cloud virtual machine so it's always ready to receive texts. You don't need to keep your computer on. Cynthia can set this up for you - see the [Deployment Guide](#deployment-guide-for-cynthia) at the bottom of this file.

Once it's deployed, Cynthia will give you the server's IP address. You'll need it for one thing:

### Tell Twilio where to forward messages
1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number
3. Scroll down to **"Messaging Configuration"**
4. Where it says **"A message comes in"**, set:
   - Select: **Webhook**
   - URL: `http://YOUR_SERVER_IP:5000/sms` (Cynthia will give you this)
   - Method: **HTTP POST**
5. Click **"Save configuration"**

**That's it - you're live!** Try texting "SIGNUP" to your Twilio number from your personal phone. You should see the signup flow begin.

---

## Step 7: Weekly Check-In Texts

The weekly texts are sent automatically every Sunday at 10am. The server handles this on its own - you don't need to do anything.

If you ever want to send the weekly texts manually (e.g. you want to change the day), ask Cynthia to run it for you

---

## Looking at the Data

When you want to see how the study is going:

1. Open a terminal
2. Navigate to the project folder
3. Type:
```
python export_data.py
```

This creates a file called **`health_data.csv`** in your project folder. You can open it in **Excel**, **Google Sheets**, or any spreadsheet app.

The CSV file contains:
- **participant_id** - a random ID (NOT their phone number)
- **week_start** - which week this response is from
- **sick** - Yes or No
- **severity** - 1-5 (only if they were sick)
- **symptoms** - what symptoms they had
- **uv_exposure** - whether they have a far-UV lamp
- **uv_hours_per_week** - how many hours they spend near one
- **zip_code** - their zip code
- **household_size** - how many people they live/work with

**This file is safe to share.** It contains zero phone numbers or identifying information.

---

## Useful Commands

From the project folder in a terminal:

| What you want to do | Command |
|---|---|
| Start the server | `python app.py` |
| Send weekly texts | `python sender.py` |
| Export data to CSV | `python export_data.py` |

## Useful Texts

From your phone, you can text these to your Twilio number:

| Text | What it does |
|---|---|
| SIGNUP | Start the signup process |
| STATUS | Check if you're enrolled |
| STOP | Opt out (stop receiving texts) |

---

## Things to Know

- **The server runs 24/7 in the cloud.** You don't need to keep your computer on. If something goes wrong, ask Cynthia.
- **Your data is stored on the cloud server** in the `data/` folder as two separate database files. Cynthia can help you back these up.
- **The `.env` file contains your secrets.** Never share it or commit it to GitHub.

---

## Deployment Guide (For Cynthia)

This section is for setting up the Google Cloud VM. Your friend doesn't need to read this.

### 1. Create a Google Cloud account and project

1. Go to https://console.cloud.google.com
2. Create a new project (e.g. "flu-tracker")
3. Make sure billing is enabled (required even for free tier)

### 2. Create the VM

1. Go to **Compute Engine > VM instances** (it may ask you to enable the API first - click Enable)
2. Click **"Create Instance"**
3. Configure:
   - **Name:** `flu-tracker`
   - **Region:** Pick one close to most participants (e.g. `us-central1`)
   - **Machine type:** `e2-micro` (this is the free tier one - it'll show "free" in the sidebar)
   - **Boot disk:** Click "Change", select **Ubuntu 22.04 LTS**, keep the default 10GB disk. Click "Select"
   - **Firewall:** Check **"Allow HTTP traffic"**
4. Click **"Create"**

### 3. Open port 5000

1. Go to **VPC Network > Firewall** in the Google Cloud console
2. Click **"Create Firewall Rule"**
3. Configure:
   - **Name:** `allow-flask`
   - **Targets:** All instances in the network
   - **Source IP ranges:** `0.0.0.0/0`
   - **Protocols and ports:** Check "TCP", enter `5000`
4. Click **"Create"**

### 4. Set up the server

SSH into the VM (click the "SSH" button next to your instance in the console), then run:

```bash
# Install Python and pip
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git

# Clone the repo
git clone https://github.com/YOUR_USERNAME/flu-tracker.git
cd flu-tracker

# Create a virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create the .env file
cp .env.example .env
nano .env
# Fill in your Twilio credentials and generate an encryption key:
# python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5. Run the server as a background service

Create a systemd service so the server starts automatically and survives reboots:

```bash
sudo tee /etc/systemd/system/flu-tracker.service << 'EOF'
[Unit]
Description=Flu Tracker SMS Server
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/flu-tracker
ExecStart=/home/$USER/flu-tracker/venv/bin/python app.py
Restart=always
RestartSec=5
EnvironmentFile=/home/$USER/flu-tracker/.env

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable flu-tracker
sudo systemctl start flu-tracker
```

Check that it's running:
```bash
sudo systemctl status flu-tracker
```

### 6. Set up the weekly sender with cron

```bash
crontab -e
```

Add this line (sends every Sunday at 10am UTC - adjust for your timezone):
```
0 10 * * 0 cd /home/$USER/flu-tracker && /home/$USER/flu-tracker/venv/bin/python sender.py
```

### 7. Configure Twilio

1. Get your VM's external IP from the Google Cloud console (shown on the VM instances page)
2. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
3. Click your number, scroll to "Messaging Configuration"
4. Set webhook to: `http://YOUR_EXTERNAL_IP:5000/sms` (POST)
5. Save

### 8. Test it

Text "SIGNUP" to the Twilio number. You should get a response within a few seconds.

### Maintenance commands

SSH into the VM and run:

```bash
# Check if server is running
sudo systemctl status flu-tracker

# View server logs
sudo journalctl -u flu-tracker -f

# Restart the server (e.g. after code changes)
sudo systemctl restart flu-tracker

# Pull latest code from GitHub
cd ~/flu-tracker && git pull && sudo systemctl restart flu-tracker

# Export data to CSV (downloads to your current directory)
cd ~/flu-tracker && source venv/bin/activate && python export_data.py

# Back up the databases (copy to Google Cloud Storage or download via SCP)
# From YOUR machine (not the VM):
# gcloud compute scp flu-tracker:~/flu-tracker/data/health.db ./health-backup.db
# gcloud compute scp flu-tracker:~/flu-tracker/data/identity.db ./identity-backup.db
```

### Cost

This should be **completely free** under Google Cloud's Always Free tier:
- 1 e2-micro VM
- 30GB standard persistent disk (we use 10GB)
- 1GB network egress per month (texts are tiny)
