import sys
from unittest.mock import MagicMock, patch, Mock
import pytest

class TestDesktopClient:

    def test_on_message_json_decode_error(self):
        """
        Verify that on_message gracefully handles invalid JSON by logging an error
        and not propagating the exception.
        """
        # Mock dependencies that are missing in the environment
        mock_deps = {
            "websocket": MagicMock(),
            "rich": MagicMock(),
            "rich.console": MagicMock(),
            "rich.panel": MagicMock()
        }

        # Apply patches to sys.modules
        # This allows us to import desktop.app.core.client even if dependencies are missing
        # and cleans up sys.modules after the test to avoid pollution.
        with patch.dict(sys.modules, mock_deps):
            # Import the module under test inside the patch context
            from desktop.app.core.client import DesktopClient

            # We also need to patch the objects inside the module.
            with patch('desktop.app.core.client.console') as mock_console, \
                 patch('desktop.app.core.client.CommandHandler') as mock_handler_cls:

                # Arrange
                server_url = "ws://testserver"
                client_id = "test_client"
                secret_key = "secret"

                # Instantiate client
                client = DesktopClient(server_url, client_id, secret_key)

                mock_ws = Mock()
                invalid_json_message = "This is not a JSON string"

                # Act
                client.on_message(mock_ws, invalid_json_message)

                # Assert
                # 1. Verify that the JSONDecodeError was caught and the error message printed
                mock_console.print.assert_any_call("[red]Invalid JSON received[/red]")

                # 2. Verify that handle() was NOT called on the handler instance
                mock_handler_instance = client.handler
                mock_handler_instance.handle.assert_not_called()
