Usage: main.py sms.data

Parses sms_dump in format sms_body@@sms_author///sms_body@@sms_author///..., translates into SmsObject, 
currently only TelecardSmsObject are available
Next step is to convert data into table and use pandas/skikit-learn to predict data