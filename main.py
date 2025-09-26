from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
import time

app = FastAPI()

todos = []
counter = 1

class TodoItem(BaseModel):
    id: Optional[int] = None
    task: str
    is_completed: bool = False

@app.middleware("http")
async def custom_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    response.headers["X-Custom-Header"] = "FastAPI DEMO"
    response.headers["X-Process-Time"] = str(round(duration, 4))
    return response

@app.get("/")
async def welcome():
    return {"message": "Welcome to the To-Do API!"}

@app.get("/health")
async def check_health():
    return {"status": "ok"}

@app.post("/todos/", response_model=TodoItem)
async def create_todo(todo: TodoItem):
    global counter
    todo.id = counter
    todos.append(todo.dict())
    counter += 1
    return todo

@app.get("/todos/{todo_id}", response_model=TodoItem)
async def read_todo(todo_id: int):
    for item in todos:
        if item["id"] == todo_id:
            return item
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.get("/todos/", response_model=List[TodoItem])
async def read_all_todos():
    return todos

@app.put("/todos/{todo_id}", response_model=TodoItem)
async def update_todo(todo_id: int, updated: TodoItem):
    for index, item in enumerate(todos):
        if item["id"] == todo_id:
            todos[index]["task"] = updated.task
            todos[index]["is_completed"] = updated.is_completed
            return todos[index]
    raise HTTPException(status_code=404, detail="To-Do item not found")

@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    global todos
    for item in todos:
        if item["id"] == todo_id:
            todos = [t for t in todos if t["id"] != todo_id]
            return {"message": f"To-Do item with ID {todo_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="To-Do item not found")
