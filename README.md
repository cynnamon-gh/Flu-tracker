# Cold & Flu Tracker

A simple text message service that asks people once a week if they've been sick. Designed to compare illness rates between people who use far-UV lamps and people who don't.

People sign up by texting your number. Every week, the service texts them to ask if they were sick. All the data is stored anonymously so no one's health info can be tied back to their phone number.

---

## What You'll Need

- A computer (Mac or Windows)
- A credit card (for Twilio - it costs about $1-2/month for the phone number, plus less than a penny per text)
- About 30 minutes for initial setup (with help from someone comfortable with computers)

---

## Step 1: Install Python

Python is the programming language this project runs on. You only need to install it once.

**On Windows:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow **"Download Python"** button
3. Run the installer
4. **IMPORTANT:** On the first screen of the installer, check the box that says **"Add Python to PATH"** (it's at the bottom - don't skip this!)
5. Click "Install Now"

**On Mac:**
1. Go to https://www.python.org/downloads/
2. Click the big yellow **"Download Python"** button
3. Open the downloaded file and follow the installer

**How to check it worked:**
1. Open a terminal:
   - **Windows:** Press the Windows key, type `cmd`, and press Enter
   - **Mac:** Press Cmd+Space, type `Terminal`, and press Enter
2. Type `python --version` and press Enter
3. You should see something like `Python 3.12.1` (the exact number doesn't matter as long as it starts with 3)

---

## Step 2: Download This Project

1. Go to the GitHub page for this project
2. Click the green **"Code"** button
3. Click **"Download ZIP"**
4. Unzip the folder somewhere you'll remember (like your Desktop)

---

## Step 3: Set Up Twilio (Your Text Message Number)

Twilio is the service that actually sends and receives text messages. Here's how to get set up:

### 3a: Create a Twilio account
1. Go to https://www.twilio.com/try-twilio
2. Sign up for a free account (you'll need to verify your email and phone number)
3. When it asks what you want to build, pick anything - it doesn't matter

### 3b: Buy a phone number
1. Once you're logged in, go to https://console.twilio.com/us1/develop/phone-numbers/manage/search
2. Make sure **"US"** is selected as the country (or whichever country you want)
3. Make sure the **"SMS"** checkbox is checked under "Capabilities"
4. Click **"Search"**
5. Pick any number from the list and click **"Buy"** (it costs about $1.15/month)
6. Confirm the purchase

### 3c: Find your credentials
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

You'll see a bunch of text scroll by as things install. Wait until it finishes (you'll see your cursor come back). If you see "Successfully installed..." at the end, you're good!

---

## Step 6: Make Your Number Publicly Reachable

When someone texts your Twilio number, Twilio needs to forward that message to your computer. For this, we use a free tool called **ngrok** that creates a secure tunnel to your machine.

### 6a: Install ngrok
1. Go to https://ngrok.com/download
2. Download the version for your computer
3. Follow their setup instructions (you'll need to create a free ngrok account)

### 6b: Start the tunnel
1. Open a terminal and type:
```
ngrok http 5000
```
2. You'll see a screen with a line that says something like:
```
Forwarding   https://abc123.ngrok-free.app -> http://localhost:5000
```
3. Copy that `https://something.ngrok-free.app` URL

**Leave this terminal window open! Don't close it.**

### 6c: Tell Twilio where to forward messages
1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click on your phone number
3. Scroll down to **"Messaging Configuration"**
4. Where it says **"A message comes in"**, set:
   - Select: **Webhook**
   - URL: paste your ngrok URL and add `/sms` at the end, so it looks like: `https://abc123.ngrok-free.app/sms`
   - Method: **HTTP POST**
5. Click **"Save configuration"**

---

## Step 7: Start the Server

1. Open a **new** terminal window (keep the ngrok one open!)
2. Navigate to the project folder (same `cd` command as Step 5)
3. Type:

```
python app.py
```

You should see something like:
```
 * Running on http://127.0.0.1:5000
```

**That's it - you're live!** Try texting "SIGNUP" to your Twilio number from your personal phone. You should see the signup flow begin.

**Leave this terminal window open while you want the service to be running.**

---

## Step 8: Send Weekly Check-In Texts

Every week (pick a consistent day, like Sunday morning), you need to send out the check-in texts to all your participants. You have two options:

### Option A: Run it manually each week
1. Open a terminal
2. Navigate to the project folder
3. Type:
```
python sender.py
```
It will send texts to everyone and tell you how many it sent.

**Remember: your server (Step 7) needs to be running when people text back!**

### Option B: Set it up to run automatically

**On Mac (using cron):**
1. Open a terminal and type `crontab -e`
2. Add this line (sends every Sunday at 10am):
```
0 10 * * 0 cd /path/to/flu-tracker && /usr/bin/python3 sender.py
```
Replace `/path/to/flu-tracker` with the actual path to your project folder.

3. Save and close the file

**On Windows (using Task Scheduler):**
1. Press the Windows key and type "Task Scheduler" - open it
2. Click **"Create Basic Task"** on the right side
3. Name it "Flu Tracker Weekly Texts"
4. Click Next, select **"Weekly"**, click Next
5. Pick Sunday, set the time to 10:00 AM, click Next
6. Select **"Start a program"**, click Next
7. For "Program/script", click Browse and find `python.exe` (usually at `C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe`)
8. For "Add arguments", type: `sender.py`
9. For "Start in", type the full path to your project folder (e.g. `C:\Users\YourName\Desktop\flu-tracker`)
10. Click Next, then Finish

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

- **The server needs to be running to receive texts.** If someone texts while the server is off, the message is lost. For a more permanent setup, you'd deploy this to a cloud server (ask Cynthia about this if needed).
- **The ngrok URL changes every time you restart ngrok.** If you restart ngrok, you'll need to update the URL in your Twilio settings (Step 6c). You can get a permanent URL with a paid ngrok plan ($8/month) or by deploying to a cloud server.
- **Your data is stored in the `data/` folder** as two separate database files. Back this folder up regularly!
- **The `.env` file contains your secrets.** Never share it or commit it to GitHub.
