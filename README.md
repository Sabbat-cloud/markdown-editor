Visual Markdown Editor - Installation Guide
This is a lightweight web application written in Python that provides a visual (WYSIWYG) Markdown editor, protected by user and password authentication.

Prerequisites
A Linux server (Debian/Ubuntu-based distributions are recommended).

Python 3.8 or higher.

pip (Python package manager).

venv (module for creating virtual environments).

1. Installation
Follow these steps to set up the application on your server.

a. Prepare the Directory and Code
First, create a directory for the application and navigate into it.

mkdir ~/markdown-editor
cd ~/markdown-editor

Now, create the app.py, hash_generator.py files, and the necessary folder structure.

b. Create and Activate the Virtual Environment
It is a best practice to isolate project dependencies in a virtual environment.

python3 -m venv venv
source venv/bin/activate

You will see (venv) at the beginning of your command prompt, indicating the environment is active.

c. Install Dependencies
Install the required Python libraries.

pip install Flask waitress Werkzeug

2. Security Configuration
User credentials are managed securely using hashes and environment variables.

a. Generate Password Hashes
Use the hash_generator.py script to convert your desired passwords into secure hashes. Run the following command for each user you want to create.

# Example for creating a hash for the password 'mySecretKey123'
python hash_generator.py 'mySecretKey123'

Copy the full hash generated in the terminal (e.g., scrypt:32768:8:1$...).

b. Set Environment Variables
For manual testing, you can export the variables directly in your terminal. Note that these variables will be lost if you close the session. We will later set them permanently in the systemd service.

# Syntax: export AUTH_USER_<username>='<generated_hash>'
export AUTH_USER_admin='the_hash_you_generated_for_admin'
export AUTH_USER_editor1='the_hash_you_generated_for_another_user'

3. Running the Application
a. Manual Execution (for testing)
With the venv environment activated and the variables exported, you can start the server:

python app.py

The application will be available at http://<your_server_IP>:3555.

b. Running as a Service (systemd) - Recommended
To run the application continuously in the background and have it restart automatically, we will create a systemd service.

1. Create the service file:

Use a text editor like nano to create the service configuration file.

sudo nano /etc/systemd/system/markdown-editor.service

2. Paste the following content:

Important! Modify the following lines:

User: Change your_user to your actual username on the server.

WorkingDirectory: Ensure the path /home/your_user/markdown-editor is correct.

Environment: Paste the environment variables here with the hashes you generated.

[Unit]
Description=Visual Markdown Editor Server
After=network.target

[Service]
# Change 'your_user' to your actual username
User=your_user
Group=www-data

# Change the path if you installed the application elsewhere
WorkingDirectory=/home/your_user/markdown-editor
ExecStart=/home/your_user/markdown-editor/venv/bin/python app.py

# --- Environment Variables for users ---
# Usernames and their hashes are defined permanently here.
# Replace the example values with your own.
Environment="AUTH_USER_admin=scrypt:32768:8:1$..."
Environment="AUTH_USER_editor1=scrypt:32768:8:1$..."

[Install]
WantedBy=multi-user.target

3. Enable and Start the Service:

Once the file is saved, run the following commands to make systemd recognize and launch your service.

# Reload the systemd configuration
sudo systemctl daemon-reload

# Enable the service to start automatically on boot
sudo systemctl enable markdown-editor.service

# Start the service right now
sudo systemctl start markdown-editor.service

4. Managing the Service
You can manage the service with the following commands:

Check status: sudo systemctl status markdown-editor.service

View logs in real-time: sudo journalctl -u markdown-editor.service -f

Restart the service: sudo systemctl restart markdown-editor.service

Stop the service: sudo systemctl stop markdown-editor.service

5. Advanced Security: Fail2Ban Integration
To protect against brute-force attacks, you can integrate fail2ban to automatically ban IPs after multiple failed login attempts.

a. Install Fail2Ban
If you don't have it installed, add it to your server:

sudo apt update
sudo apt install fail2ban

b. Create the Log File
The application needs a place to write its logs. Create the log file and give the application user permission to write to it.

sudo touch /var/log/markdown-editor.log
sudo chown your_user:www-data /var/log/markdown-editor.log
sudo chmod 664 /var/log/markdown-editor.log

Remember to replace your_user with your actual username (the same one you used in the systemd service file).

c. Create the Fail2Ban Filter
This filter tells fail2ban how to recognize a failed login attempt in our log file.

Create a new filter file:

sudo nano /etc/fail2ban/filter.d/markdown-editor.conf

Paste the following content:

[Definition]
failregex = ^.* Failed login attempt for user '.*' from IP '<HOST>'$
ignoreregex =

d. Create the Fail2Ban Jail
This jail configuration links our filter to an action (banning the IP).

Create a new jail file:

sudo nano /etc/fail2ban/jail.d/markdown-editor.local

Paste the following content. This configuration will ban an IP for 10 minutes after 3 failed attempts within a 10-minute window.

[markdown-editor]
enabled = true
port = 3555
filter = markdown-editor
logpath = /var/log/markdown-editor.log
maxretry = 3
findtime = 600
bantime = 600

e. Restart and Verify
Apply the new configuration by restarting both your application and the fail2ban service.

# Restart your app to apply logging changes
sudo systemctl restart markdown-editor.service

# Restart fail2ban to load the new jail
sudo systemctl restart fail2ban

You can check the status of your new jail with:

sudo fail2ban-client status markdown-editor

Now, any IP that fails to log in 3 times will be automatically blocked by your server's firewall.
