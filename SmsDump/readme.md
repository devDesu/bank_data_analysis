Simple Android App which dumps all sms objects from "Telecard" sender to http server

sms_server.py just recieves POST request and saves data from it
Usage sms_server.py port
Important! sms_server revrites old data, make sure you've renamed/moved "saved.data"