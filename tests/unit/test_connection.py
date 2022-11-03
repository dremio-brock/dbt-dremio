import pytest
from unittest.mock import patch
from dbt.exceptions import FailedToConnectException
from dbt.adapters.dremio.credentials import DremioCredentials
from dbt.adapters.dremio.api.rest.error import DremioRequestTimeoutException
from dbt.adapters.dremio.connections import DremioConnectionManager


class TestRetryConnection:
    @patch("dbt.adapters.dremio.api.rest.endpoints._post")
    @patch("dbt.contracts.connection.Connection")
    # When you nest patch decorators the mocks are passed in to the decorated function in bottom up order.
    def test_connection_retry(
        self,
        mocked_connection_obj,
        mocked_post_func,
    ):
        # Arrange
        TOTAL_CONNECTION_ATTEMPTS = (
            DremioConnectionManager.DEFAULT_CONNECTION_RETRIES + 1
        )

        mocked_connection_obj.credentials.software_host = ""
        mocked_connection_obj.credentials.cloud_host = None
        mocked_connection_obj.credentials.port = 9047
        mocked_connection_obj.credentials.use_ssl = False

        mocked_post_func.side_effect = DremioRequestTimeoutException(
            msg="Request timeout: Test", original_exception="408 original exception"
        )

        # Act
        with pytest.raises(FailedToConnectException) as exception_info:
            DremioConnectionManager.open(connection=mocked_connection_obj)

        # Assert
        assert mocked_post_func.call_count == TOTAL_CONNECTION_ATTEMPTS