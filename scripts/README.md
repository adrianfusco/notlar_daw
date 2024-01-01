# Scripts

## update_database.py

In case we need to have a new attribute to any of our models, we need a way to update the existing database based on the new attribute.

This script will automate the migration process.

Example:

Let's imagine we are in development environment and we need to update:

- `notlar` database
- `notes` table
- New field `note_date` of type DATE

The arguments would be:

```bash
$ -> python3 update_database.py postgresql://notlar:notlar@$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' notlar_db):5432/notlar notes note_date DATE
Upgrade successful for table 'notes' and column 'note_date'.
```
