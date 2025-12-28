DROP TABLE IF EXISTS employees CASCADE;
DROP TABLE IF EXISTS departments CASCADE;

CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department INT NOT NULL REFERENCES departments(id) ON DELETE SET NULL,
    salary INT CHECK (salary >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_salary ON employees(salary);

INSERT INTO departments (department) VALUES
('Engineering'),
('HR'),
('Sales');

INSERT INTO employees (name, department, salary) VALUES
('Alice', 1, 90000),
('Bob', 1, 72000),
('Charlie', 2, 54000),
('Diana', 3, 61000),
('Eve', 1, 88000),
('Frank', 3, 58000),
('Grace', 2, 50000);
