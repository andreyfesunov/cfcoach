from fastapi import FastAPI
from rest.routers.auth import router as auth_router
import uvicorn


app = FastAPI()

app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)
