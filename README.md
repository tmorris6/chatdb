# **ChatDB**

Natural Language Interface for MySQL

## **Overview**

ChatDB is a command-line tool that allows users to explore, query, and update MySQL databases using natural language. The system translates user input into SQL based on a provided database schema, executes the query, and returns results directly from the database.

This project focuses on reducing the overhead of writing SQL for common data tasks while maintaining transparency and control over query execution.

## **Example Queries**

The system supports questions such as:

- What tables are in the database?

- What columns are in the movies table?

- Show the number of crimes per area.

- List the top 5 highest-rated games by meta score.

## **Tools & Technologies**

- Python

- OpenAI API (GPT-based models)

- MySQL

- mysql-connector-python

- tabulate

## **Data & Schemas**

This repository focuses on query generation and execution logic. Database schemas are included for context, but the actual datasets are not provided.

The example schemas represent crime records, movie metadata, and video game data.
