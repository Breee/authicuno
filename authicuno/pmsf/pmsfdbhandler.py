import sqlalchemy
import re
from utility.globals import LOGGER
from sqlalchemy.orm import sessionmaker
from typing import Union, List
from database.dbhandler import DbHandler, transaction_wrapper
from discord import  Member


class PmsfDBHandler(DbHandler):
    def __init__(self, host, database, port, user, password, dialect, driver):
        super(PmsfDBHandler, self).__init__(host, database, port, user, password, dialect, driver)

    def generate_query(self,  member_id : int, access_level : int, member_name: str):
        member_name = re.sub(r'[^\x00-\x7F]+', '', member_name)
        query = f"""INSERT INTO users (id,user,access_level,expire_timestamp,login_system) VALUES ({member_id},\"{member_name}\",{access_level},1,'discord') ON DUPLICATE KEY UPDATE user=VALUES(user),access_level=VALUES(access_level),login_system=VALUES(login_system);"""
        return query

    @transaction_wrapper
    def update_member(self, member: Member, access_level : int) -> None:
        LOGGER.info(f"Updating: {member} to lvl {access_level}")
        self.session.execute(self.generate_query(member.id, access_level, f'{member.name}#{member.discriminator}'))

    def update_members(self, access_map: dict) -> None:
        query_bundle = []
        for member, access_lvl in access_map.items():
            self.update_member(member,access_lvl)

    @transaction_wrapper
    def get_members(self):
        res = self.session.execute("SELECT id,user,access_level FROM users")
        return [f'{user}: {access_level}' for id,user,access_level in res]

if __name__ == '__main__':
    db = PmsfDBHandler(host="localhost", user="pmsf", password="bestpw", port="1339", database="pmsf",
                       dialect="mysql", driver="mysqlconnector")
    db.update_member(377196211054051339, 4, "Bree#2002")
    print("\n".join(db.get_members()))


