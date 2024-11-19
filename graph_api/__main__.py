import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from graph_api import api_config, routes

app = FastAPI()
app.include_router(routes.router)
origins = api_config["origins"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    uvicorn.run(app, host=api_config["host"], port=api_config["port"])
    # uvicorn.run(app, host=api_config["host"], port=api_config["port"],ssl_certfile="/usr/local/share/ca-certificates/143.233.226.88.crt", ssl_keyfile="/usr/local/share/ca-certificates/143.233.226.88.key")
