Usage: main.py sms.data [file.cfg]

cfg file format:

Key1 Value1

Key2 Value2
...

Only CN key and Salary_filter are accepted now

Parses sms_dump in format sms_body@@sms_author///sms_body@@sms_author///..., translates into SmsObject, 
currently only TelecardSmsObject are available

Some pandas magick are already done.

Next step is to use skikit-learn to predict data
