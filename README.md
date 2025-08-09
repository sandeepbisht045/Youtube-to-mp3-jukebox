A Django web app which simply takes youtube urls and merge the content into a single .mp3 file generally made for creating jukebox of songs
Developed in python 3.10 with django framework
In the project folder there is a file .environ_var where you need to provide Secret key and youtube api key in order to run this project in the below provided format
YOUTUBE_API_KEY="APIKEY"
SECRET_KEY="SECRETKEY"

Also first create virtual environment with below command for python 3.10
python3.10 -m venv venv
Activate it
install modules using requirements.txt

Before you run the new script, you will need to:

Get a Google API Key:

Go to the Google Cloud Console.

Create a new project.

Enable the "YouTube Data API v3".

Create credentials for an "API key".

Copy this key. You'll paste it into the .environ_var file.