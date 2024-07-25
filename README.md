# TensorFlirt: Automate Your Swiping Adventure 🤖💕

### Swiping is so last year—let the robots handle it!

TensorFlirt revolutionizes your dating app experience by training a neural network on your specific Tinder preferences and then automating the swiping process. 

> **Heads up!** 🚨 Using TensorFlirt likely violates Tinder's terms of service. Proceed at your own risk!

### Getting Started

#### Prerequisites
- **TensorFlow**: Make sure it's installed and running. GPU support enhances performance but isn't a must.
- **Virtual Environment**: Create and activate one. If this sounds daunting, TensorFlirt might be a tad advanced for you.
- **Dependencies**: Install all necessary packages with:
  ```bash
  pip install -r requirements.txt
  ```

### How to Use TensorFlirt

#### Authentication Token
First off, snag an `X-Auth-Token` from the Tinder web app by inspecting a request. Insert this token into a `.env` file in the project directory like so:
```plaintext
AUTH_TOKEN=xxxxx-xxx-xxxxxxx-xxxxx
```

#### Farm Images
To train your neural network, you’ll need plenty of images—about 2,000 should do the trick. Luckily, you can fetch these from Tinder's API in under an hour without hitting rate limits. Run:
```bash
$ python farm_photos.py
```
This script saves photos into `images/downloaded`, plus organizes them into subfolders for original photos, faces and full bodies, setting you up nicely for the next steps.
Original photos aren't required and consume a lot of space, so I might add a flag to disable downloading them in the future. 

The script will also save every profile it comes across in the `images/downloaded/users` directory. They can be read into a `User` class but I haven't implemented it either.

#### Classify Your Swipes
You need to manually swipe—sort your photos into 'yes' or 'no' piles, which will be later used to train the neural net.

The photos are moved from the `downloaded` directory into `images\classified`. This means that farming and classifying can be done at the same time!
```bash
$ python classify_photos.py
```
Swipe with the left and right arrow keys, and undo with `ctrl + z`.

#### Train Your AI
Now, let the magic happen. This script *should* train and produce two models in the `model\` directory, one for faces and one for bodies.
It runs fairly quickly on a dedicated GPU, so CPU training might take a while but should be feasible.
```bash
$ python train.py
```
Tinker with the model settings if you’re feeling brave. Aiming for about 0.75 accuracy usually works well in my experience.

#### Launch TensorFlirt
Let your AI take the reins:
```bash
$ python tensor_flirt.py
```
Watch as it finds matches for you. Now, if only it could help you move out of your mum’s basement...

### Future Enhancements

There’s plenty of room for improvement! A user interface to monitor and adjust the AI's decisions in real-time would be a great start. Also, introducing features like auto-messaging with an advanced language model could take your dating life to the next level!

Interested in collaborating? Drop me a line—we’re excited to push this forward together!

Embark on your automated dating journey with TensorFlirt and spend your newfound free time doing, well, anything else! 🚀💘
