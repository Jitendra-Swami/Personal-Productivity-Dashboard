from flask import Flask, render_template, redirect, request, flash, jsonify

from dotenv import load_dotenv
import os

import psycopg

load_dotenv()

app = Flask(__name__)
app.secret_key = "dev-secret-key"



def get_postgres_db():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )



name = "Jitendra"
goal = "Learn HTML"


@app.route("/")
def home():

    db_tasks = get_tasks_from_db()

    priority_order = {
        "high": 1,
        "medium": 2,
        "low": 3
    }

    db_tasks.sort(
        key=lambda task: priority_order.get(task["priority"], 2)
    )

    completed = 0

    for task in db_tasks:
        if task["done"]:
            completed += 1

    total = len(db_tasks)

    if total > 0:
        percentage = round((completed / total) * 100)
    else:
        percentage = 0

    return render_template(
        "index.html",
        name=name,
        goal=goal,
        tasks=db_tasks,
        percentage=percentage,
        completed=completed
    )



@app.route("/toggle/<int:task_id>")
def toggle_task(task_id):

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT done FROM tasks WHERE id = %s",
                (task_id,)
            )

            task = cur.fetchone()

            if task:
                new_status = not task[0]

                cur.execute(
                    "UPDATE tasks SET done = %s WHERE id = %s",
                    (new_status, task_id)
                )

        db.commit()

    finally:
        db.close()

    return redirect("/")



    
@app.route("/delete/<int:task_id>")
def delete_task(task_id):

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s",
                (task_id,)
            )

        db.commit()

    finally:
        db.close()

    return redirect("/")



@app.route("/add", methods=["POST"])
def add_task():

    task_name = request.form["task"].strip()
    if not task_name:
        flash("Task name cannot be empty.")
        return redirect("/")

    if len(task_name) > 100:
        return redirect("/")

    priority = request.form["priority"].lower()

    if priority not in ["low", "medium", "high"]:
        return redirect("/")

    
    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (name, done, priority) VALUES (%s, %s, %s)",
                (task_name, False, priority)
            )

        db.commit()

    finally:
        db.close()


    return redirect("/")


@app.route("/edit/<int:task_id>")
def edit_task(task_id):

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, priority FROM tasks WHERE id = %s",
                (task_id,)
            )

            task = cur.fetchone()

    finally:
        db.close()

    return render_template(
        "edit.html",
        task=task
    )


@app.route("/edit/<int:task_id>", methods=["POST"])
def update_task(task_id):

    task_name = request.form["task"].strip()

    if not task_name:
        flash("Task name cannot be empty.")
        return redirect(f"/edit/{task_id}")

    if len(task_name) > 100:
        flash("Task name cannot exceed 100 characters.")
        return redirect(f"/edit/{task_id}")
    
    priority = request.form["priority"].lower()

    if priority not in ["low", "medium", "high"]:
        flash("Invalid priority.")
        return redirect(f"/edit/{task_id}")

    
    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET name = %s, priority = %s WHERE id = %s",
                (task_name, priority, task_id)
            )

        db.commit()

    finally:
        db.close()


    return redirect("/")


def get_tasks_from_db():

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, done, priority FROM tasks ORDER BY id"
            )
            rows = cur.fetchall()

        tasks = []

        for row in rows:
            tasks.append({
                "id": row[0],
                "name": row[1],
                "done": row[2],
                "priority": row[3]
            })

        return tasks

    finally:
        db.close()


@app.route("/api/tasks", methods=["GET"])
def api_get_tasks():

    tasks = get_tasks_from_db()

    return jsonify(tasks)

@app.route("/api/tasks/<int:task_id>", methods=["GET"])
def api_get_task(task_id):

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "SELECT id, name, done, priority FROM tasks WHERE id = %s",
                (task_id,)
            )

            task = cur.fetchone()

    finally:
        db.close()

    if task:
        return jsonify({
            "id": task[0],
            "name": task[1],
            "done": task[2],
            "priority": task[3]
        })

    return jsonify({
        "error": "Task not found"
    }), 404


@app.route("/api/tasks", methods=["POST"])
def api_create_task():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "name" not in data:
        return jsonify({
        "error": "Task name is required"
    }), 400

    if not data["name"].strip():
        return jsonify({
        "error": "Task name cannot be empty"
    }), 400

    if len(data["name"]) > 100:
        return jsonify({
        "error": "Task name cannot exceed 100 characters"
    }), 400

    if "priority" not in data:
        return jsonify({
        "error": "Priority is required"
    }), 400

    if data["priority"] not in ["low", "medium", "high"]:
            return jsonify({
        "error": "Invalid priority"
    }), 400

    
    db = get_postgres_db()

    
    try:
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (name, done, priority) VALUES (%s, %s, %s) RETURNING id",
                (data["name"], False, data["priority"])
            )

            task_id = cur.fetchone()[0]

        db.commit()

    finally:
        db.close()



    return jsonify({
    "id": task_id,
    "name": data["name"],
    "done": False,
    "priority": data["priority"]
}), 201


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
def api_update_task(task_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Request body is required"
        }), 400

    if "name" not in data:
        return jsonify({
            "error": "Task name is required"
        }), 400

    if not isinstance(data["name"], str) or not data["name"].strip():
        return jsonify({
            "error": "Task name cannot be empty"
        }), 400

    if len(data["name"]) > 100:
        return jsonify({
            "error": "Task name cannot exceed 100 characters"
        }), 400

    if "priority" not in data:
        return jsonify({
            "error": "Priority is required"
        }), 400

    if data["priority"] not in ["low", "medium", "high"]:
        return jsonify({
            "error": "Invalid priority"
        }), 400

    if "done" not in data or not isinstance(data["done"], bool):
        return jsonify({
            "error": "Done status must be true or false"
        }), 400

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                """
                UPDATE tasks
                SET name = %s, priority = %s, done = %s
                WHERE id = %s
                RETURNING id
                """,
                (data["name"].strip(), data["priority"], data["done"], task_id)
            )

            task = cur.fetchone()

            if not task:
                return jsonify({
                    "error": "Task not found"
                }), 404

        db.commit()

        return jsonify({
            "id": task_id,
            "name": data["name"].strip(),
            "priority": data["priority"],
            "done": data["done"]
        }), 200

    finally:
        db.close()



@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def api_delete_task(task_id):

    db = get_postgres_db()

    try:
        with db.cursor() as cur:
            cur.execute(
                "DELETE FROM tasks WHERE id = %s RETURNING id",
                (task_id,)
            )

            deleted_task = cur.fetchone()

        if not deleted_task:
            return jsonify({
                "error": "Task not found"
            }), 404

        db.commit()

        return jsonify({
            "message": "Task deleted successfully"
        }), 200

    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)