import argparse
import json
import logging
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
import yaml


def setup_logging(log_file: Path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # file handler
    fh = logging.FileHandler(log_file, mode="w", encoding="utf-8")
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # logging to stdout
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)
    return logger


def read_config(config_path: Path):
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)

        # verifying fields
        if not isinstance(cfg, dict):
            raise ValueError("configuration is not a dict")
        
        for field in ["seed", "window", "version"]:
            if field not in cfg:
                raise ValueError(f"missing '{field}' in configuration")
        return cfg
    except Exception as e:
        raise


def main():
    parser = argparse.ArgumentParser(description="MLOps pipeline")
    parser.add_argument("--input", required=True, help="input CSV file")
    parser.add_argument("--config", required=True, help="YAML config file")
    parser.add_argument("--output", required=True, help="Metrics output JSON file")
    parser.add_argument("--log-file", required=True, help="Log file path")
    args = parser.parse_args()

    out_metrics = {}
    start_time = time.time()

    try:
        log_path = Path(args.log_file)
        logger = setup_logging(log_path)

        logger.info("Job started")

        # load config
        cfg = read_config(Path(args.config))
        out_metrics["version"] = cfg.get("version")
        logger.info(f"Config loaded: seed={cfg['seed']}, window={cfg['window']}, version={cfg['version']}")

        # set seed
        np.random.seed(cfg["seed"])

        # load data
        csv_path = Path(args.input)
        if not csv_path.exists():
            raise FileNotFoundError(f"Input file {csv_path} does not exist")
        
        df = pd.read_csv(csv_path)
        if df.empty:
            raise ValueError("CSV file is empty")
        
        required_column = ["close"]
        for col in required_column:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' missing from input")
        logger.info(f"Data loaded: {len(df)} rows")

        # rolling mean
        window = cfg["window"]
        df["rolling_mean"] = df["close"].rolling(window=window, min_periods=1).mean()
        logger.info(f"Rolling mean calculated with window={window}")

        # signal generation
        df["signal"] = (df["close"] > df["rolling_mean"]).astype(int)
        logger.info("Signals generated")

        # metrics
        rows_processed = len(df)
        signal_rate = float(df["signal"].mean())
        latency_ms = int((time.time() - start_time) * 1000)

        # ordered metrics dictionary
        out_metrics = {
            "version": cfg.get("version"),
            "rows_processed": rows_processed,
            "metric": "signal_rate",
            "value": round(signal_rate, 4),
            "latency_ms": latency_ms,
            "seed": cfg["seed"],
            "status": "success",
        }

        logger.info(f"Metrics: signal_rate={signal_rate:.4f}, rows_processed={rows_processed}")
        logger.info(f"Job completed successfully in {latency_ms}ms")

        # writing metrics
        with open(args.output, "w", encoding="utf-8") as out:
            json.dump(out_metrics, out, indent=2)

        # To stdout
        print(json.dumps(out_metrics, indent=2))
        sys.exit(0)

    except Exception as e:
        err_msg = str(e)
        logging.error(err_msg)

        # building error output
        version_val = out_metrics.get("version") or "v1"
        out_metrics = {
            "version": version_val,
            "status": "error",
            "error_message": err_msg
        }
        
        try:
            with open(args.output, "w", encoding="utf-8") as out:
                json.dump(out_metrics, out, indent=2)
        except Exception:
            pass

        print(json.dumps(out_metrics, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
