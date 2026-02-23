import logging
from qaai_system.infra import logging_utils


def test_get_logger_and_log(tmp_path, monkeypatch):
    monkeypatch.setattr(logging_utils, "cfg", None)  # disable cfg import if any
    log_file = tmp_path / "system.log"

    logger = logging.getLogger("test_logger")
    logger.handlers.clear()  # reset
    handler = logging.FileHandler(log_file)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    logger.info("Hello, world!")

    handler.close()
    with open(log_file, "r") as f:
        contents = f.read()
    assert "Hello, world!" in contents


def test_log_data_source_info(caplog):
    logger = logging.getLogger("test_data_source")
    bars = [{"ts": 1, "open": 100, "source": "YAHOO"}]
    logging_utils.log_data_source(logger, "RELIANCE", bars)
    assert "RELIANCE using data source: YAHOO" in caplog.text


def test_log_data_source_warning(caplog):
    logger = logging.getLogger("test_data_source_warn")
    bars = [{"ts": 1, "open": 100}]  # no source
    logging_utils.log_data_source(logger, "RELIANCE", bars)
    assert "data source unknown" in caplog.text
