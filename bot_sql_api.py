import sqlite3
import os
from tabulate import tabulate as tb


def print_t(seq):
    print(tb(seq, tablefmt="fancy_grid"))


def try_except_decorator(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, *kwargs)
        except Exception as e:
            print(" *** ERROR *** : ", e, " in ", func.__name__)
            return -1

    return wrapper


class SpamDB:
    """
    Api for work with the Spam Data Base
    """

    def __init__(self, db_name="spam_db.sqlite", auto_save=False):
        """
        :param db_name: name of DB file
        :param auto_save: should PhoneDB save changes on destroy
        """
        self.__auto_save = auto_save
        self.__default_classes_names = ('Spam', 'Fraud', 'Threats', 'Advertisement', 'Other')

        cur_dir = os.getcwd()
        db_exists = os.path.exists(cur_dir + '/' + db_name)
        print('------------------------')
        if db_exists:
            print('Loading DB...')
        else:
            print('Creating DB...')

        # Creating Spam DB if not exists
        self.SQL_connection = sqlite3.connect(db_name, check_same_thread=False)
        self.SQL_cursor = self.SQL_connection.cursor()

        if not db_exists:
            res0 = self.__create_tables()
            res1 = self.__insert_default_classes(self.__default_classes_names)
            res2 = self.__define_triggers()
            if res0 == -1 or res1 == -1 or res2 == -1:
                os.remove(cur_dir + '/' + db_name)
                self.__auto_save = False
                print("System: can not create DB")
                print('------------------------')
                exit()

        print('DB loading has succeeded')
        print('------------------------')

    def __del__(self):
        if self.__auto_save:
            self.save()
        self.SQL_connection.close()

    @try_except_decorator
    def save(self) -> int:
        """
        Save changes to DB file
        :return 1 - success, (-1) - error
        """
        self.SQL_connection.commit()
        print("System: DB saved")
        return 1

    @try_except_decorator
    def __define_triggers(self) -> int:
        """
        Create SQL Triggers on Reviews table for updating Phone's fields
        :return: 1 - success, (-1) - error
        """
        # when INSERT
        self.SQL_cursor.execute(
            '''
            CREATE TRIGGER counter_insert 
            AFTER INSERT ON Reviews
            BEGIN
                UPDATE Phones
                SET reviews_number = (reviews_number + 1), common_class_id = (SELECT class_id FROM (SELECT class_id, MAX(counter) FROM
                                                                                 (SELECT class_id,
                                                                                  COUNT(class_id) AS counter 
                                                                                  FROM Reviews
                                                                                  WHERE phone_id = NEW.phone_id
                                                                                  GROUP BY class_id))
                                                                               )
                WHERE id = NEW.phone_id;
                
                
            END;
            ''')

        # when DELETE
        self.SQL_cursor.execute(
            '''
            CREATE TRIGGER counter_delete 
            AFTER DELETE ON Reviews
            BEGIN
                UPDATE Phones
                SET reviews_number = (reviews_number - 1), common_class_id = (SELECT class_id FROM (SELECT class_id, MAX(counter) FROM
                                                                                 (SELECT class_id,
                                                                                  COUNT(class_id) AS counter 
                                                                                  FROM Reviews
                                                                                  WHERE phone_id = OLD.phone_id
                                                                                  GROUP BY class_id))
                                                                               )
                WHERE id = OLD.phone_id;
                
                DELETE FROM Phones
                WHERE reviews_number <= 0;
            END;
            ''')

        return 1

    def __create_tables(self) -> int:
        """
        Creates two tables Persons and Phone
        which are related by an phone owner id (one to many)
        :return None (void):
        """
        self.SQL_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Reviews 
            (id INTEGER PRIMARY KEY,
            phone_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            comment TEXT,
            reviewer_id INTEGER NOT NULL,
            foreign key (phone_id) references Phones(id),
            foreign key (class_id) references Classes(id))
            ''')
        self.SQL_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Phones 
            (id INTEGER PRIMARY KEY,
            phone TEXT NOT NULL,
            reviews_number INTEGER NOT NULL,
            common_class_id INTEGER NOT NULL,
            foreign key (common_class_id) references Classes(id))
            '''
        )
        self.SQL_cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS Classes 
            (id INTEGER PRIMARY KEY,
            name TEXT NOT NULL)
            '''
        )
        # create index
        self.SQL_cursor.execute(
            '''
            CREATE UNIQUE INDEX idx_phones 
            ON Phones (phone)
            '''
        )
        return 1

    @try_except_decorator
    def __insert_default_classes(self, default_list: tuple):
        for index, class_name in enumerate(default_list):
            values = (index, class_name)
            self.SQL_cursor.execute(
                '''
                INSERT INTO Classes
                VALUES (?, ?)
                ''', values
            )
        return 1

    @try_except_decorator
    def find_phone(self, phone_number: str):
        """
        Search records in Phones table based on 'phone' field (text)
        :param phone_number: text representation of phone number
        :return: tuple - row of Phones table, if phone exists, else -1
        """
        result = self.SQL_cursor.execute(
            '''
            SELECT Phones.id, Phones.phone, Phones.reviews_number, Classes.name 
            FROM Phones, Classes
            WHERE phone = ? AND Phones.common_class_id = Classes.id
            ''', (phone_number,)
        ).fetchall()
        if len(result) == 0:
            return -1
        else:
            return result[0]

    @try_except_decorator
    def find_reviews(self, phone_id: int):
        """
        Search reviews of phone
        :param phone_id: what phone the reviews are about
        :return: list of reviews if exist else -1
        """
        result = self.SQL_cursor.execute(
            '''
            SELECT Classes.name, Reviews.comment FROM Reviews, Classes
            WHERE Reviews.phone_id = ? AND Reviews.class_id = Classes.id
            ''', (phone_id,)
        ).fetchall()
        if len(result) == 0:
            return -1
        return result

    @try_except_decorator
    def find_personal_reviews(self, reviewer_id: int):
        """
        Search reviews of the reviewer
        :param reviewer_id: who are the author of the reviews
        :return: list of reviews if exist else -1
        """
        result = self.SQL_cursor.execute(
            '''
            SELECT Phones.phone, Classes.name, Reviews.comment, Reviews.id
            FROM Reviews, Classes, Phones
            WHERE Reviews.reviewer_id = ? 
              AND Reviews.class_id = Classes.id 
              AND Reviews.phone_id = Phones.id
            ''', (reviewer_id,)
        ).fetchall()
        if len(result) == 0:
            return -1

        return result

    @try_except_decorator
    def find_class_name(self, class_id: int) -> str:
        """
        Search class name
        :param class_id: what class name have to be found
        :return: name
        """
        result = self.SQL_cursor.execute(
            '''
            SELECT name FROM Classes
            WHERE id = ?
            ''', (class_id,)
        ).fetchall()
        return result[0][0]

    @try_except_decorator
    def find_phone_classes(self, phone_id):
        """
        Find all classes of phone which have been mentioned in reviews
        :param phone_id: id of phone
        :return: list of classes
        """
        result = self.SQL_cursor.execute(
            '''
            SELECT DISTINCT Classes.name FROM Reviews, Classes
            WHERE Reviews.phone_id = ? AND Reviews.class_id = Classes.id
            ''', (phone_id,)
        ).fetchall()
        result = tuple(map(lambda x: x[0], result))
        return result

    @try_except_decorator
    def insert_review(self, review_info: tuple) -> int:
        """
        Insert new review (auto check phone existence)
        :param review_info - tuple (phone_number, class_id, comment, reviewer_id)
        :return: inserted person ID - success, (-1) - error
        """
        phone_search = self.find_phone(review_info[0])
        if phone_search == -1:
            phone_id = self.__insert_phone((review_info[0], review_info[1]))
            if phone_id == -1:
                print('Failed to insert phone: ', review_info)
                return -1
        else:
            phone_id = phone_search[0]
        # update info
        review_info = (phone_id, review_info[1], review_info[2], review_info[3])

        self.SQL_cursor.execute(
            '''
            INSERT INTO Reviews
            VALUES ((SELECT MAX(id) from Reviews) + 1, ?, ?, ?, ?)
            ''', review_info
        )
        # trigger

        return self.__reviews_max_index()

    @try_except_decorator
    def update_review(self, review_info: tuple):
        """
        Update review record
        :param review_info: tuple (review_id, new_comment)
        :return: 1 - success, (-1) - error
        """
        phone_id = self.SQL_cursor.execute(
            '''
            SELECT phone_id FROM Reviews
            WHERE id = ?
            ''', (review_info[0],)
        ).fetchall()[0][0]

        self.SQL_cursor.execute(
            '''
            UPDATE Reviews
            SET comment = ?
            WHERE id = ?
            ''', (review_info[1], review_info[0])
        ).fetchall()

        return 1

    def __insert_phone(self, phone_info: tuple) -> int:
        """
        Insert phone information to the DB
        :param phone_info - tuple (phone_num, initial_class_id)
        :return: inserted phone ID - success, (-1) - error
        """
        self.SQL_cursor.execute(
            '''
            INSERT INTO Phones
            VALUES ((SELECT MAX(id) from Phones) + 1, ?, 0, ?)
            ''', phone_info
        )
        return self.__phones_max_index()

    @try_except_decorator
    def delete_review(self, review_id):
        """
        Deletes review and recalculates phone record
        :param review_id: what review have to be deleted
        :return: 1 - success, (-1) - error
        """
        phone_id = self.SQL_cursor.execute(
            '''
            SELECT phone_id FROM Reviews
            WHERE id = ?
            ''', (review_id,)
        ).fetchall()
        phone_id = int(phone_id[0][0])

        self.SQL_cursor.execute(
            '''
            DELETE FROM Reviews
            WHERE id = ?
            ''', (review_id,)
        )

        return 1

    def __delete_phone(self, phone_id) -> int:
        """
        Delete the phone record
        :param phone_id: the phone to delete
        :return: 1 - success, (-1) - error
        """
        self.SQL_cursor.execute(
            '''
            DELETE FROM Phones
            WHERE id = ?
            ''', (phone_id,)
        )
        return 1

    def __phones_length(self) -> int:
        """
        function to calculate the length of Phones table
        :return: number of rows in the table
        """
        self.SQL_cursor.execute(
            '''
            SELECT COUNT(id) from Phones
            '''
        )
        return int(self.SQL_cursor.fetchone()[0])

    def __phones_max_index(self) -> int:
        """
        function to calculate new index for Phones table
        :return: new index
        """
        self.SQL_cursor.execute(
            '''
            SELECT MAX(id) from Phones
            '''
        )
        return int(self.SQL_cursor.fetchone()[0])

    def __reviews_length(self) -> int:
        """
        function to calculate the length of Phones table
        :return: number of rows in the table
        """
        self.SQL_cursor.execute(
            '''
            SELECT COUNT(id) from Reviews
            '''
        )
        return int(self.SQL_cursor.fetchone()[0])

    def __reviews_max_index(self) -> int:
        """
        function to calculate new index for Phones table
        :return: new index
        """
        self.SQL_cursor.execute(
            '''
            SELECT MAX(id) from Reviews
            '''
        )
        return int(self.SQL_cursor.fetchone()[0])

    @try_except_decorator
    def _read_all_phones(self):
        return self.SQL_cursor.execute(
            '''
            SELECT * FROM Phones
            '''
        ).fetchall()

    @try_except_decorator
    def _read_all_reviews(self):
        return self.SQL_cursor.execute(
            '''
            SELECT * FROM Reviews
            '''
        ).fetchall()

    @try_except_decorator
    def _read_all_classes(self):
        return self.SQL_cursor.execute(
            '''
            SELECT * FROM Classes
            '''
        ).fetchall()


def print_all(data_base):
    print('          PRINT          ')
    print('Phones')
    print_t(data_base._read_all_phones())
    print('Reviews')
    print_t(data_base._read_all_reviews())
    print('Classes')
    print_t(data_base._read_all_classes())

#db = SpamDB()
#print_all(db)
# db.delete_review(3)
# print_all(db)
# res = db.find_phone_classes(1)
# print(res)


# res = db.find_phone('88005553535')
# print(type(res), res)
# print_t([res])
# res = db.find_reviews(res[1])
# print(type(res), res)
# print_t(res)
# review_info = ('89107991200', 1, 'assholes', 12345)
# res = db.insert_review(review_info)
# print(type(res), res)
# db.r(1)

# res = db.find_personal_reviews(1)
# print(type(res), res)
# print_t(res)

# res = db.update_review((1, 1, 'ads!'))
# db.delete_review(1)

# print_all(db)
# db.save()

