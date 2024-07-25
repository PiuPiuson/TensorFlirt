# TensorFlirt
### Swiping is boring, let the robots do it

TensorFlirt is a tool that allows you to train a neural net on your local Tinder preferences, then use it to automate swiping.

### How to setup
* Make sure you have `TensorFlow` up and running (GPU support is not necessary but recommended)
* This project relies on `tkinter` which some python versions ship without. 
  In Ubuntu installing it is as simple as `$ sudo apt install python3-tk`
* Create a virtual environment and activate it (if you don't know how to do that this project is probably too advanced for you)
* Install requirements: `pip install -r requirements.txt`

### How to use
#### Auth Token
Now for the good stuff. First thing we need is an `X-Auth-Token` which can be obtained by snooping an API request from the tinder webapp.
Create a `.env` file in the repo directory and place the token inside
`AUTH_TOKEN = xxxxx-xxx-xxxxxxx-xxxxx`

#### Farm Images
In order to train the neural net you're going to need loads of images (ideally ~2000)
Fortunately, the Tinder API allows us to get them in less than an hour without being rate limited!
To do that just run `$ python farm_photos.py`

The script will pull photos from your recommendations and place them into the `images/downloaded` folder.
It will also create two more folders, one with cropped faces and one with the user's body. You're going to use both of them to train the models later.

#### Swipe one last time
Time to swipe for one last time! You need to classify the photos into left and right swipes.
Run `$ python classify_photos.py` and swipe using the left and right arrow keys. You can undo a swipe with `ctrl + z`

#### Train the AI
This is simple, time consuming and grossly automated.
`$ python train.py`

Feel free to play around with the model if you feel confident, in my experience ~0.75 accuracy is good enough

#### Sit back and let her rip
Run `$ python tensor_flirt.py` and watch the AI get you quality matches.
If only there was a way to get you out of your mum's basement as well...


### Further work
This has a lot of potential, auto messaging using an LLM being the low hanging fruit.
Get in touch if you want to collaborate!
