# What is this?

A python script you can run to automatically toggle on/off your tp link tapo p100 plugs depending on how much power you are using and producing according to your solaredge inverter.

*You can run this on a server because unlike most p100 power plug control scripts, this one works remotely.*

# Setup
- Name your plugs like this in the tapo app: `PV-1000W-Heating` (Use the wattage of the device plugged into the plug instead of 1000W)
- Clone this repo
- Run `pip install -r requirements.txt`
- Create `authentication.py` with these variables:
  - solar_edge_api_key = "Your solaredge api key - found on the solaredge website > admin > access > api access" 
  - solar_edge_site_id = "Your solaredge site id"
  - tplink_email = "The email you use to login to the tp link tapo app"
  - tplink_password = "Your tp link tapo app account password"
- Adjust `settings.py` if you'd like. (See the comments in that file for an explanation of the parameters)
- Run `python main.py`
  - If you want to automatically run it on a server or raspberry pi, you can create a systemd service like this:
    - `sudo nano /etc/systemd/system/solaredge-tplink-control.service`
    
          [Unit]
          Description=Runs the solaredge-tplink-control python program
          After=network.service
  
          [Service]
          Type=simple
          ExecStart=/usr/bin/python3 /home/aulig/solaredge-tplink-control/main.py
          WorkingDirectory=/home/aulig/solaredge-tplink-control
          User=aulig
          StandardOutput=append:/home/aulig/solaredge-tplink-control/systemdexecution.log
          StandardError=append:/home/aulig/solaredge-tplink-control/systemdexecution.log
        
          [Install]
          WantedBy=multi-user.target

    - `sudo chmod 644 /etc/systemd/system/solaredge-tplink-control.service`
    - `sudo systemctl daemon-reload`
    - `sudo systemctl enable solaredge-tplink-control.service`
    - `sudo reboot`
    - Check if it worked: `sudo systemctl status solaredge-tplink-control.service`
