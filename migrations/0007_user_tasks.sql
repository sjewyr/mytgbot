CREATE TABLE user_tasks(
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    reward BIGINT NOT NULL,
    exp_reward BIGINT NOT NULL,
    lvl_required BIGINT NOT NULL,
    cost BIGINT NOT NULL,
    length INT NOT NULL
);

INSERT INTO user_tasks (name, reward, exp_reward, lvl_required, cost, length)
VALUES
('Сходить нахрен', 90, 4, 1, 10, 2),
('Получить в рыло', 170, 10, 1, 70, 2),
('Сдать калл на цвет.мет.', 800, 110, 4, 250, 10),
('Лизинг души дьяволу', 1700, 180, 4, 1000, 10);
