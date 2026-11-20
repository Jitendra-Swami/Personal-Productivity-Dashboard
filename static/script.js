const button = document.getElementById("motivateButton");
const message = document.getElementById("motivation");

const messages = [
    "Keep going! 🔥",
    "You're making progress!",
    "One step at a time!",
    "Don't stop now!",
    "You've got this!"
];

button.addEventListener("click", function () {
    const randomIndex = Math.floor(Math.random() * messages.length);
    message.textContent = messages[randomIndex];
});


const productivity = document.getElementById("productivity");

console.log(productivity.textContent);


// Shared task data
let data = [];


const taskList = document.getElementById("api-tasks");

function updateProductivity() {
    const completed = data.filter(task => task.done).length;
    const total = data.length;

    const percentage = total > 0
        ? Math.round((completed / total) * 100)
        : 0;

    document.getElementById("task-counter").textContent =
        `${completed} / ${total} completed`;

    document.getElementById("productivity").textContent =
        `Productivity: ${percentage}%`;

    document.getElementById("progress-bar").style.width =
        `${percentage}%`;
}

function renderTask(task) {
    const li = document.createElement("li");

    li.className = "task-item";
    li.dataset.taskId = task.id;

    // Task checkbox
    const checkbox = document.createElement("input");

    checkbox.type = "checkbox";
    checkbox.checked = task.done;
    checkbox.dataset.id = task.id;

    // Task name
    const taskName = document.createElement("span");

    taskName.textContent = task.name;

    if (task.done) {
        taskName.classList.add("completed");
    }

    // Task priority
    const priority = document.createElement("span");

    priority.className = `priority ${task.priority}`;
    priority.textContent =
        task.priority.charAt(0).toUpperCase() +
        task.priority.slice(1);

    // Delete button
    const deleteButton = document.createElement("button");

    deleteButton.textContent = "Delete";
    deleteButton.className = "delete-btn";

    // Edit button
    const editButton = document.createElement("button");

    editButton.textContent = "Edit";
    editButton.className = "edit-btn";

    // Checkbox change handler
    checkbox.addEventListener("change", async function () {
        const previousDone = task.done;

        checkbox.disabled = true;

        try {
            const response = await fetch(
                `/api/tasks/${task.id}`,
                {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        name: task.name,
                        priority: task.priority,
                        done: checkbox.checked
                    })
                }
            );

            const result = await response.json().catch(() => null);

            if (!response.ok) {
                throw new Error(
                    result?.error || `HTTP error: ${response.status}`
                );
            }

            task.done = checkbox.checked;
            taskName.classList.toggle("completed", task.done);

            updateProductivity();

            console.log("Updated:", result);

        } catch (error) {
            checkbox.checked = previousDone;

            console.error("Update error:", error);
            document.getElementById("api-message").textContent =
                error.message;

        } finally {
            checkbox.disabled = false;
        }
    });

    // Assemble the task
    li.appendChild(checkbox);
    li.appendChild(taskName);
    li.appendChild(priority);
    li.appendChild(deleteButton);
    li.appendChild(editButton);

    taskList.appendChild(li);
}

// One parent click listener for Edit and Delete
taskList.addEventListener("click", async function (event) {
    const editButton = event.target.closest(".edit-btn");
    const deleteButton = event.target.closest(".delete-btn");

    // Ignore clicks that are not on either button
    if (!editButton && !deleteButton) {
        return;
    }

    const taskItem = event.target.closest(".task-item");

    if (!taskItem || !taskList.contains(taskItem)) {
        return;
    }

    const taskId = Number(taskItem.dataset.taskId);

    if (!Number.isInteger(taskId)) {
        console.error("Invalid task ID");
        return;
    }

    // Edit task
    if (editButton) {
        window.location.href = `/edit/${taskId}`;
        return;
    }

    // Delete task
    deleteButton.disabled = true;

    try {
        const response = await fetch(`/api/tasks/${taskId}`, {
            method: "DELETE"
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                result?.error || `HTTP error: ${response.status}`
            );
        }

        const taskIndex = data.findIndex(
            task => Number(task.id) === taskId
        );

        if (taskIndex !== -1) {
            data.splice(taskIndex, 1);
        }

        taskItem.remove();
        updateProductivity();

        console.log("Delete result:", result);

        document.getElementById("api-message").textContent =
            "Task deleted successfully!";

    } catch (error) {
        console.error("Delete error:", error);

        document.getElementById("api-message").textContent =
            error.message;

        deleteButton.disabled = false;
    }
});




async function loadTasks() {

    try {

const response = await fetch("/api/tasks");

if (!response.ok) {
    throw new Error(`HTTP error! Status: ${response.status}`);
}


const tasks = await response.json();

        data = tasks;

        console.log(data);

        const taskList = document.getElementById("api-tasks");

        taskList.innerHTML = "";

        data.forEach(task => {
            renderTask(task);
        });


        document.getElementById("api-message").textContent =
            "API connected!";

    }

    catch (error) {
    console.error("Failed to Load Task:", error);

    document.getElementById("api-message").textContent =
        error.message ;
}
} 

loadTasks();

// Add task form

const taskForm = document.getElementById("task-form");

const submitButton = taskForm.querySelector('button[type="submit"]');

taskForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    submitButton.disabled = true;

    const taskName = taskForm.elements["task"].value;
    const priority = taskForm.elements["priority"].value;


    const taskData = {
        name: taskName,
        priority: priority
    };


    
    try {
        const response = await fetch("/api/tasks", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(taskData)
        });

        const result = await response.json().catch(() => null);

        if (!response.ok) {
            throw new Error(
                result?.error || `HTTP error: ${response.status}`
            );
        }

        console.log("Created task:", result);

        data.push(result);

        taskForm.reset();

        renderTask(result);

        document.getElementById("api-message").textContent =
            "Task created successfully!";

    } catch (error) {
        console.error("Create error:", error);

        document.getElementById("api-message").textContent =
            error.message;  
    }finally {
    submitButton.disabled = false;
}



    console.log("Task:", taskName);
    console.log("Priority:", priority);
    console.log("Form submitted");

});

const heading = document.getElementById("dashboard-title");

heading.textContent = "Welcome Back!";
heading.classList.add("highlight-heading");

const motivateButton = document.getElementById("motivateButton");

console.log(motivateButton);    

let messageIndex = 0;

motivateButton.addEventListener("click", function () {
    heading.textContent = messages[messageIndex];

    heading.classList.toggle("highlight-active");

    messageIndex = (messageIndex + 1) % messages.length;
});