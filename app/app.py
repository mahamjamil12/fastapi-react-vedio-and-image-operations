# User will send a file to our api and api will upload it to imagekit
# then we will grab the url and save it to our database and serve that to our user on the frontend


from fastapi import FastAPI,HTTPException,File,UploadFile,Form,Depends
from app.schemas import PostCreate,PostResponse
from app.db import Post, create_db_and_tables,get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from app.images import imagekit
from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# the data we return from our end points should be python dictionary
# or pydantic object
# why we return data in python dictionary because when we create apis
# we work wth json (dealing with data across the web)
# JSON - > Javascript object notation


# @app.get("/hellow-world")
# def hello_world():
#     return {"msg":"hello world"}


@app.post("/upload")
async def upload_file(
    file:UploadFile = File(...),
    caption: str = Form(""),
    session: AsyncSession= Depends(get_async_session)

):
    temp_file_path = None

    try: 
        # make a name to temporary file that ends in whatenver the file upload
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=os.path.splitext(file.filename)[1]
        ) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)


        # upload the file and give it to imagekit and then it will give us the result
        upload_result = imagekit.upload_file(
            file=open(temp_file_path, "rb"),
            file_name=file.filename,
            options=UploadFileRequestOptions(
                use_unique_file_name= True,
                tags= ["backend-upload"]
            )
        )

        if upload_result.response_metadata.http_status.http_status_code == 200:
                 # creating post
                post = Post(
                    caption=caption,
                    url=upload_result.url,
                    file_type="video" if file.content_type.startswith("video/") else "image",
                    file_name= "dummy name"
                )
                # adding it to database like stagging
                session.add(post)
                # and then commiting it to save
                await session.commit()
                await session.refresh(post)
                return post
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))
    finally:
         if temp_file_path and os.path.exists(temp_file_path):
              os.unlink(temp_file_path)
         file.file.close()

@app.get("/feed")
async def get_feed(
    session:AsyncSession= Depends(get_async_session)
):
    result = await session.execute(select(Post).order_by(Post.created_at.desc()))
    # accessing all the vales and making a list
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id":str(post.id),
                "caption":post.caption,
                "url":post.url,
                "file_type":post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat()
            }
        )

    return {"posts": posts_data}
