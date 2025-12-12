# hytale-username-checker
Check Hytale username availability for reservations

This is not a good program. It has only been tested on my machine. I wrote it in like 20 minutes so I could get a cool username.

It does not query APIs or do anything smart. It just straight up opens a web browser and checks if there is an X or a ✓ next to the name

Put your stuff in a .env file:
```
# Hytale Account Credentials
HYTALE_USERNAME=your_email@example.com
HYTALE_PASSWORD=your_password_here

#Hytale Login Token
HYTALE_TOKEN=123456789ABC

# ChromeDriver Path
PATH_CHROMEDRIVER=C:\\path\\to\\chromedriver.exe

# Chrome User Data Directories (for separate browser sessions)
PATH_USERDATA_1=C:\\path\\to\\ChromeDriver1
PATH_USERDATA_2=C:\\path\\to\\ChromeDriver2
```

Install the requirements:
```
selenium>=4.39.0
python-dotenv>=1.0.0
```

