CREATE TABLE user_user_tasks(
    user_id INTEGER,
    task_id INTEGER,
    PRIMARY KEY (user_id, task_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES user_tasks(id)
)
