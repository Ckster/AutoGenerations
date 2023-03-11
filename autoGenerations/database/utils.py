from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from database.config import DATABASE_URL

Base = declarative_base()


def make_engine():
    return create_engine(DATABASE_URL)


def overwrite_relationship_list(session, parent_table, relationship_attr: str, new_objects):
    old_objects = getattr(parent_table, relationship_attr)
    updated_ids = [i.id for i in new_objects]

    # Delete the records not in new objects
    existing_ids_to_delete = []
    for object in old_objects:
        if object.id not in updated_ids:
            existing_ids_to_delete.append(object.id)

    for id in existing_ids_to_delete:
        session.query(parent_table).query(parent_table.id == id).delete()

    # Set the new relationship
    setattr(parent_table, relationship_attr, new_objects)


def merge_lists(list1, list2):
    return list1 + [i for i in list2 if i not in list1]
