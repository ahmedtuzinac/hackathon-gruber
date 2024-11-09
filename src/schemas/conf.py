import os
import sys

from pydantic import BaseModel
from typing import Optional, AnyStr, Dict, List
import dotenv

dotenv.load_dotenv()


class DatabaseConfig(BaseModel):
    """
    Configuration settings for the database connection.

    Attributes:
        db_name (str): The name of the database.
        db_port (int): The port number for the database connection.
        db_host (str): The hostname or IP address of the database server.
        db_password (str): The password for the database user.
    """

    db_name: AnyStr
    db_port: int
    db_host: AnyStr
    db_user: AnyStr
    db_password: AnyStr

    def __init__(
            self,
            /,
            **kwargs
    ) -> object:
        """
        Initializing DatabaseConfig model, with feature of checking if values
        exists in environments.
        :param kwargs:
        """

        _testmode: bool = kwargs.get('_testmode', False)
        _dbconf: Dict = self._configuration_db(
            _testmode=_testmode
        )
        ...
        kwargs = _dbconf
        super().__init__(**kwargs)

    def _configuration_db(
            self,
            _testmode: bool
    ) -> Dict:
        """
        This method gets values from environment files which are necessary for establishing
        connection with a database. If some value is missing it raises detailed error.

        :param _testmode (bool): Checks if application is started in test mode.
        :return: Dictionary of values from environment file with necessary data for
                 configuring database.
        """
        _conf: Dict = dict()

        varss: tuple = (
            'DB_NAME',
            'DB_HOST',
            'DB_PORT',
            'DB_USER',
            'DB_PASSWORD',
        )

        missing_values: List = list()

        for var in varss:
            value: AnyStr | int = os.getenv(var, None)
            if not value: missing_values.append(var)
            _conf[var.lower()] = value

        if len(missing_values) != 0:
            for _v in missing_values:
                print('{}: missing in environment file!\n'.format(_v))

            sys.exit(1)

        if _testmode:
            _conf['db_name'] = 'test_' + _conf['db_name']

        return _conf
