import sqlalchemy
from utility.globals import LOGGER
from sqlalchemy.orm import sessionmaker
import core.models as coremodels
from typing import Union, List

from database.dbhandler import DbHandler, transaction_wrapper


class CoreDBHandler(DbHandler):
    def __init__(self, host, database, port, user, password, dialect, driver):
        super(CoreDBHandler, self).__init__(host, database, port, user, password, dialect, driver)
        self.base = coremodels.Base
        self.base.metadata.create_all(self.engine)

    @transaction_wrapper
    def set_prefix(self, server_id : int, prefix : str) -> None:
        try:
            existing_prefix: coremodels.ServerSetting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
            existing_prefix.prefix = prefix
        except sqlalchemy.orm.exc.NoResultFound:
            new_prefix = coremodels.ServerSetting(server_id=server_id, prefix=prefix, moderator_roles=[])
            self.session.add(new_prefix)

    @transaction_wrapper
    def get_prefix(self, server_id: int) -> Union[str, None]:
        try:
            server_setting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
        except sqlalchemy.orm.exc.NoResultFound:
            return None
        return server_setting.prefix

    @transaction_wrapper
    def reset_prefix(self, server_id: int) -> None:
        try:
            server_setting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
            server_setting.prefix = None
        except sqlalchemy.orm.exc.NoResultFound:
            LOGGER.warning(f"No Settings for server_id {server_id}")

    @transaction_wrapper
    def get_moderator_roles(self, server_id: int) -> List[int]:
        try:
            server_setting: coremodels.ServerSetting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
            if server_setting.moderator_roles:
                return list(server_setting.moderator_roles)
        except sqlalchemy.orm.exc.NoResultFound:
            pass
        return []

    @transaction_wrapper
    def add_moderator_roles(self, server_id, roles):
        try:
            server_setting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
            if server_setting.moderator_roles:
                server_setting.moderator_roles = list(set(server_setting.moderator_roles + roles))
            else:
                server_setting.moderator_roles = list(set(roles))
        except sqlalchemy.orm.exc.NoResultFound:
            new_server_setting = coremodels.ServerSetting(prefix="", server_id=server_id, moderator_roles=list(set(roles)))
            self.session.add(new_server_setting)

    @transaction_wrapper
    def reset_moderator_roles(self, server_id):
        try:
            server_setting = self.session.query(coremodels.ServerSetting).filter(coremodels.ServerSetting.server_id == server_id).one()
            server_setting.moderator_roles = []
        except sqlalchemy.orm.exc.NoResultFound:
            LOGGER.warning(f"No Settings for server_id {server_id}")


if __name__ == '__main__':
    db = CoreDBHandler(host="localhost", user="pollman", password="bestpw", port="3307", database="polldb",
                       dialect="mysql", driver="mysqlconnector")
