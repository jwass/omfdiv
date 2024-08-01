# omfdiv

Overture Maps divisions data TUI

<img width="1208" alt="Screenshot 2024-08-01 at 5 04 16 PM" src="https://github.com/user-attachments/assets/747e2fe2-d575-4d7d-aa1a-7bc5af6af682">


## Build the divisions duckdb database

```
$ poetry run omfdiv builddb
```

This will download the Overture divisions data and create a "divisions.duckdb"
file in the current working directory. This database file will be used by the
UI to dynamically generate the tree.

Note: The data retrieved on S3 is publicly accessible but if you have AWS credentials
in your environment that are expired, this command can fail. Ensure either you have
no keys/credentials set, or the ones that are active have not expired.

## Run the UI

```
$ poetry run omfdiv ui
```
