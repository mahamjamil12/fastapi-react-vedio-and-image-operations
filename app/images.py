from dotenv import load_dotenv
from imagekitio import ImageKit
import os

# load env will look for the values in the env and load them
load_dotenv()

imagekit = ImageKit(
    # os.getenv will find the presence of these var and load them in code
    private_key=os.getenv("IMAGEKIT_PRIVATE_KEY"),
    public_key=os.getenv("IMAGEKIT_PUBLIC_KEY"),
    url_endpoint=os.getenv("IMAGEKIT_URL")
)
