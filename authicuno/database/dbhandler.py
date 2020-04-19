import sqlalchemy
from utility.globals import LOGGER
from sqlalchemy.orm import sessionmaker


def transaction_wrapper(func):
    def _wrap_func(*args, **kwargs):
        self = args[0]
        session = sessionmaker(bind=self.engine, expire_on_commit=False)

        # new session.   no connections are in use.
        self.session = session()
        try:
            # execute transaction statements.
            res = func(*args, **kwargs)
            # commit.  The pending changes above
            # are flushed via flush(), the Transaction
            # is committed, the Connection object closed
            # and discarded, the underlying DBAPI connection
            # returned to the connection pool.
            self.session.commit()
        except Exception as err:
            LOGGER.critical(err)
            # on rollback, the same closure of state
            # as that of commit proceeds.
            self.session.rollback()
            raise
        finally:
            # close the Session.  This will expunge any remaining
            # objects as well as reset any existing SessionTransaction
            # state.  Neither of these steps are usually essential.
            # However, if the commit() or rollback() itself experienced
            # an unanticipated internal failure (such as due to a mis-behaved
            # user-defined event handler), .close() will ensure that
            # invalid state is removed.
            self.session.close()
        return res

    return _wrap_func


class DbHandler(object):

    def __init__(self, host, database, port, user, password, dialect, driver):
        self.host = host
        self.database = database
        self.port = port
        self.user = user
        self.password = password
        self.dialect = dialect
        self.driver = driver
        self.conn = None
        self.cursor = None
        self.engine = sqlalchemy.create_engine(
                '%s+%s://%s:%s@%s:%s/%s' % (dialect, driver, user, password, host, port, database),
                pool_pre_ping=True)
        self.session = None
        self.metadata = sqlalchemy.MetaData()
        self.base = None


if __name__ == '__main__':
    db = DbHandler(host="localhost", user="pollman", password="bestpw", port="3307", database="polldb",
                   dialect="mysql", driver="mysqlconnector")
