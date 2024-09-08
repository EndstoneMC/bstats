import pytest
from pathlib import Path
import uuid
import tomlkit
from endstone_bstats import MetricsConfig  # Make sure to import the class from the appropriate module


@pytest.fixture
def temp_config_file(tmp_path: Path):
    """
    Fixture that creates a temporary config file.
    """
    return tmp_path / "config.toml"


def test_initialization_creates_file(temp_config_file):
    """
    Test whether the MetricsConfig properly creates a config file if it does not exist.
    """
    config = MetricsConfig(temp_config_file, default_enabled=True)

    # Check if the config file was created
    assert temp_config_file.exists()
    assert config.did_exist_before is False


def test_loading_existing_config(temp_config_file):
    """
    Test loading an existing config file.
    """

    # Manually create a config file
    config_content = tomlkit.document()
    config_content["enabled"] = True
    config_content["server-uuid"] = str(uuid.uuid4())
    config_content["log-errors"] = True
    config_content["log-sent-data"] = True
    config_content["log-response-status-text"] = True

    with open(temp_config_file, "w", encoding="utf-8") as f:
        tomlkit.dump(config_content, f)

    config = MetricsConfig(temp_config_file, default_enabled=False)

    assert config.enabled is True
    assert config.log_errors_enabled is True
    assert config.log_sent_data_enabled is True
    assert config.log_response_status_text_enabled is True
    assert config.did_exist_before is True


def test_malformed_config_creates_new_config(temp_config_file):
    """
    Test if it recreates the config file on malformed content.
    """

    # Create a malformed config file
    config_content = tomlkit.document()
    config_content["enabled"] = True

    with open(temp_config_file, "w", encoding="utf-8") as f:
        tomlkit.dump(config_content, f)

    config = MetricsConfig(temp_config_file, default_enabled=True)

    # Check if the config file was recreated
    assert config.server_uuid is not None
    assert config.did_exist_before is True


def test_default_config_values(temp_config_file):
    """
    Test default config values if a new config file is created.
    """
    config = MetricsConfig(temp_config_file, default_enabled=True)

    assert config.enabled is True
    assert config.log_errors_enabled is False
    assert config.log_sent_data_enabled is False
    assert config.log_response_status_text_enabled is False


def test_config_values_after_updating(temp_config_file):
    """
    Test whether the loaded config values are correct after updating some fields.
    """
    default_enabled = False
    config = MetricsConfig(temp_config_file, default_enabled=default_enabled)

    with open(temp_config_file, "r", encoding="utf-8") as f:
        config_data = tomlkit.load(f)

    config_data["enabled"] = not default_enabled
    config_data["log-errors"] = True
    config_data["log-sent-data"] = True
    config_data["log-response-status-text"] = True

    with open(temp_config_file, "w", encoding="utf-8") as f:
        tomlkit.dump(config_data, f)

    config.load_config()  # Reload the configuration

    assert config.enabled == (not default_enabled)
    assert config.log_errors_enabled is True
    assert config.log_sent_data_enabled is True
    assert config.log_response_status_text_enabled is True
