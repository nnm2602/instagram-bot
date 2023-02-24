# instagram-bot

## HOW TO USE
### SETTING UP: 
To set everything up, change the following files: 

1. Reddit_headers.json: put your authorization id from your own reddit api in the right spot 
ex: "bearer XYZ"

2. Publitio/data.py: Create an account on [Publitio](https://publit.io/) and place your key and secret into the appropriate spots inside the file.

3. User/_data.py: connect to your the facebook api developer account and place your app_id as well as your app_secret in the appropriate places.

4. Reddit/data.py: connect your reddit api account and place the necessary information in the file. 

### Using the software:

```python
import viralscrape as bot 
bot.upload("r/Unexpected",1,"top",0)
```
In this specific instance, 1 is for the maximum number of post that we would like to post and 0 is our default starting point. 
Change "r/Unexpected" to your desired subreddit and "hot" to whatever category you would like the engine to search through.
